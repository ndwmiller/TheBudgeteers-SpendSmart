from kivy.app import App


class SettingsBackend:
    def load_settings_from_db(self):
        app = App.get_running_app()
        db = app.db

        theme = db.get_setting('theme')
        font = db.get_setting('font')
        alerts = db.get_setting('alerts')
        reminders = db.get_setting('reminders')
        self.current_theme = theme or 'light'

        if theme == 'light':
            self.ids.light_mode_cb.active = True
        else:
            self.ids.dark_mode_cb.active = True
        app.apply_theme(self.current_theme, rebuild=False)

        font_map = {'small': 'Small', 'medium': 'Medium', 'large': 'Large'}
        self.ids.font_spinner.text = font_map.get(font, 'Medium')
        self.ids.budget_toggle.active = (alerts == 'True')
        self.ids.bill_toggle.active = (reminders == 'True')
        app.apply_font_size(font)
        app.apply_notification_settings(
            alerts=(alerts == 'True'),
            reminders=(reminders == 'True'),
        )

    def set_theme(self, theme):
        self.current_theme = theme
        app = App.get_running_app()
        app.db.set_setting('theme', theme)
        app.apply_theme(theme)

    def set_font_size(self, size_name):
        app = App.get_running_app()
        if app and getattr(app, 'db', None):
            size_name = size_name.lower()
            app.db.change_font(size_name)
            app.apply_font_size(size_name)

    def toggle_budget_alerts(self, active):
        app = App.get_running_app()
        if app and getattr(app, 'db', None):
            app.db.set_setting('alerts', str(active))
            app.apply_notification_settings(alerts=active)

    def toggle_bill_reminders(self, active):
        app = App.get_running_app()
        if app and getattr(app, 'db', None):
            app.db.set_setting('reminders', str(active))
            app.apply_notification_settings(reminders=active)

    def clear_data(self):
        App.get_running_app().db.clear_data()

    def reset_defaults(self):
        app = App.get_running_app()
        db = app.db
        db.restore_defaults()
        self.ids.dark_mode_cb.active = False
        self.ids.light_mode_cb.active = True
        self.ids.font_spinner.text = 'Medium'
        self.ids.budget_toggle.active = True
        self.ids.bill_toggle.active = False
        self.current_theme = 'light'
        app.apply_theme('light')
        app.apply_font_size('medium')
        app.apply_notification_settings(alerts=True, reminders=False)
