from kivy.metrics import sp
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.stacklayout import StackLayout

from modules.dbactions import connectToDatabase, closeDatabaseConnection
from modules.global_vars import cameras_dict, SECONDARY_COLOR, BG_COLOR, detection_dict, actions_dict

rules_container: FloatLayout
last_addnewrule: FloatLayout
title_label: Label


class RulesContainer(StackLayout):
    def __init__(self, **kwargs):
        super(RulesContainer, self).__init__(**kwargs)
        global rules_container
        rules_container = self
        self.load_rules()
        
    def load_rules(self):
        db, cursor = connectToDatabase()
        
        cursor.execute("SELECT name, rules, actions WHERE rules!=''")
        results = cursor.fetchall()
        for row in results:
            name = row[0]
            rules_str = row[1].split()
            actions_str = row[2].split()
            for i in range(len(rules_str)):
                rule_name = detection_dict.get(int(rules_str[i]))
                action_name = actions_dict.get(int(actions_str[i]))
            rule_creator = NewRuleCreator(isGenerated=True, camera_name=name, rule_name=rule_name, action_name=action_name)
            self.add_widget(rule_creator)
            
        closeDatabaseConnection(db, cursor)
class SpinnerButtons(SpinnerOption):
    def __init__(self, **kwargs):
        super(SpinnerButtons, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = SECONDARY_COLOR
        self.font_size: sp(24)
        self.color = BG_COLOR


class CamerasListButton(Spinner):
    def __init__(self, **kwargs):
        super(CamerasListButton, self).__init__(**kwargs)
        self.values = cameras_dict.values()
        self.option_cls = SpinnerButtons


class ActionsButton(Spinner):
    def __init__(self, **kwargs):
        super(ActionsButton, self).__init__(**kwargs)
        self.values = detection_dict.values()
        self.option_cls = SpinnerButtons


class SaveButton(Button):
    actionsListButton = ObjectProperty()
    detectionListButton = ObjectProperty()
    camerasListButton = ObjectProperty()

    def __init__(self, **kwargs):
        super(SaveButton, self).__init__(**kwargs)

    def on_press(self):
        db, cursor = connectToDatabase()
        for cID, value in cameras_dict.items():
            if value == self.camerasListButton.text:
                cameraID = cID
        for dID, value in detection_dict.items():
            if value == self.detectionListButton.text:
                detectionID = dID
        for aID, value in actions_dict.items():
            if value == self.actionsListButton.text:
                actionID = aID
        cursor.execute("UPDATE cameras SET rules=concat(rules, '%s'), actions=concat(actions, '%s') WHERE generated_id=%s", (detectionID, actionID, cameraID))
        db.commit()
        actionsListButton.disabled = True
        detectionListButton.disabled = True
        camerasListButton.disabled = True
        self.parent.remove_widget(self)
        closeDatabaseConnection(db, cursor)


class DeleteRule(Button):
    actionsListButton = ObjectProperty()
    detectionListButton = ObjectProperty()
    camerasListButton = ObjectProperty()

    def __init__(self, **kwargs):
        super(DeleteRule, self).__init__(**kwargs)

    def on_press(self):
        db, cursor = connectToDatabase()
        for cID, value in cameras_dict.items():
            if value == self.camerasListButton.text:
                cameraID = cID
        for dID, value in detection_dict.items():
            if value == self.detectionListButton.text:
                detectionID = dID
        for aID, value in actions_dict.items():
            if value == self.actionsListButton.text:
                actionID = aID
        
        
        cursor.execute("SELECT rules, actions from cameras WHERE generated_id=%s", (cameraID,))
        results = cursor.fetchone()
        rules_str = results[0]
        actions_str = results[1]
        cursor.execute("UPDATE cameras SET rules=%s, actions=%s WHERE generated_id=%s", (rules_str.replace(str(detectionID), ''), actions_str.replace(str(actionID), ''), cameraID))
        closeDatabaseConnection(db, cursor)


class ActionsButton2(Spinner):
    def __init__(self, **kwargs):
        super(ActionsButton2, self).__init__(**kwargs)
        self.values = actions_dict.values()
        self.option_cls = SpinnerButtons


class NewRuleCreator(FloatLayout):
    actionsListButton = ObjectProperty()
    detectionListButton = ObjectProperty()
    camerasListButton = ObjectProperty()
    isGenerated = False
    camera_name = None
    rule_name = None
    action_name = None
    def __init__(self, **kwargs):
        super(NewRuleCreator, self).__init__(**kwargs)

    def on_kv_post(self, base_widget):
        delete_rule = self.ids.delete_rule
        delete_rule.bind(on_press=self.delete_pressed)
        if isGenerated:
            actionsListButton.text = action_name
            detectionListButton.text = rule_name
            camerasListButton.text = camera_name
            actionsListButton.disabled = True
            detectionListButton.disabled = True
            camerasListButton.disabled = True
            

    def delete_pressed(self, widget):
        self.parent.remove_widget(self)
        global title_label
        title_label.active_rules -= 1


class AddNewRule(FloatLayout):
    def __init__(self, **kwargs):
        super(AddNewRule, self).__init__(**kwargs)
        global last_addnewrule
        last_addnewrule = self


class TitleLabel(Label):
    active_rules = NumericProperty(0)

    def __init__(self, **kwargs):
        super(TitleLabel, self).__init__(**kwargs)
        global title_label
        title_label = self


class AddNewRule_Button(Button):
    def __init__(self, **kwargs):
        super(AddNewRule_Button, self).__init__(**kwargs)

    def on_press(self):
        rl = NewRuleCreator()
        global rules_container, last_addnewrule, title_label
        rules_container.remove_widget(last_addnewrule)
        rules_container.add_widget(rl)
        rules_container.add_widget(last_addnewrule)
        title_label.active_rules += 1
