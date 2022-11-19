import sys, os, json
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QCheckBox, QComboBox
from PyQt6.QtGui import QIntValidator, QDoubleValidator, QValidator, QIcon
from PyQt6 import uic
from typing import Dict, List, Optional, Any, Iterable
from main import AVAIALBLE_TIMEFRAMES, BOT_DETAILS

# BOT_DETAILS['BOT_NAME'] should be changed to 'python main.py' when developing, and only
# used when building program to exe
TO_RUN:str = 'python main.py' if os.path.isfile('main.py') else f"{BOT_DETAILS['BOT_NAME']}-cli"

class BotApplication(QWidget):
    GUR_PATH:str = os.path.join('GUIs', 'bot-gui.ui')
    SAVE_CONFIG_DIR:str = 'saved_config' 
    SAVE_CONFIG_FILENAME:str = 'config.json' 
    SAVE_CONFIG_PATH:str = os.path.join(SAVE_CONFIG_DIR, SAVE_CONFIG_FILENAME)

    def __init__(self):
        super(BotApplication, self).__init__()
        uic.loadUi(self.GUR_PATH, self)

        self.setWindowIcon(QIcon(BOT_DETAILS['BOT_ICON']))
        self.setWindowTitle(
            f"{BOT_DETAILS['BOT_NAME']} - Trade Bot. Version - ({BOT_DETAILS['VERSION']}). {BOT_DETAILS['COPYRIGHTS_INFO']}")

        self.strategy_title.setStyleSheet(
            '''
            font-size:20px;
            font-weight:bold;
            '''
        )

        self.auth_title.setStyleSheet(
            '''
            font-size:20px;
            font-weight:bold;
            '''
        )

        self._strategies = ['tolu', 'engulf', 'rejection', 'composite']
        self.populateCombobox('strategy', self._strategies)
        self.populateCombobox('timeframe', AVAIALBLE_TIMEFRAMES.keys())
        self.setConfig() #set saved config params
        self.start_button.clicked.connect(self.startEvent)
        self.help_button.clicked.connect(self.showHelpMenu)


    def populateCombobox(self, combobox_name:str, items:Iterable):
        if not hasattr(self, combobox_name) : return
        getattr(self, combobox_name).clear()
        for item in items:
            getattr(self, combobox_name).addItem(item)

    
    def setConfig(self):
        if not os.path.isfile(self.SAVE_CONFIG_PATH): return

        with open(self.SAVE_CONFIG_PATH) as f:
            configs:dict = json.load(f)
            for key in configs.keys():
                if hasattr(self, key):
                    if isinstance(getattr(self, key), QLineEdit):
                        getattr(self, key).setText(configs[key])

                    elif isinstance(getattr(self, key), QCheckBox):
                        getattr(self, key).setChecked(configs[key])

                    elif isinstance(getattr(self, key), QComboBox):
                        getattr(self, key).setCurrentText(configs[key])

    
    def saveConfig(self, params:dict):
        if not os.path.isdir(self.SAVE_CONFIG_DIR):
            os.mkdir(self.SAVE_CONFIG_DIR)

        params:dict = params.copy()
        if 'password' in params.keys():
            params.pop('password')
        return json.dump(params, open(self.SAVE_CONFIG_PATH, 'w'), indent = 6)


    def validateInput(self, input:Any, rule:Optional[QValidator])->bool:
        if len(input) == 0:return False
        if rule is None:return True
        return rule.validate(input, 10)[0] == QValidator.State.Acceptable
    

    def showHelpMenu(self):
        command:str = f'start /B start cmd /k {TO_RUN} -h'
        os.system(command)

    def startEvent(self):
        params:Dict[tuple] = {
             #logins
            'login' : (self.login.text(), None),
            'password' : (self.password.text(), None),
            'server' : (self.server.text(), None),

            #parameters
            'symbol' : (self.symbol.text(), None), 
            'volume' : (self.volume.text(), QDoubleValidator()),
            'deviation' : (self.deviation.text(), QIntValidator()), 
            'unit_pip': (self.unit_pip.text(), QDoubleValidator()),
            'default_sl': (self.default_sl.text(), QDoubleValidator()),
            'max_sl_dist': (self.max_sl_dist.text(), QDoubleValidator()),
            'sl_trail': (self.sl_trail.text(), QDoubleValidator()),
            'default_tp': (self.default_tp.text(), QDoubleValidator()),
            'sr_likelihood':(self.sr_likelihood.text(), QDoubleValidator()),
            'sr_threshold':(self.sr_threshold.text(), QDoubleValidator()),
            'period':(self.period.text(), QIntValidator())
        }

        #validate input parameters
        validation_list:List[bool] = []
        for key in params.keys():
            is_valid:bool = self.validateInput(*params[key])
            validation_list.append(is_valid)
            if not is_valid:
                getattr(self, key).setText('')
                getattr(self, key).setPlaceholderText("Required / incorrect")

        #save input details
        if all(validation_list) and self.save_config.isChecked():
            config = {k:v[0] for k, v in params.items()}
            config['use_atr'] = self.use_atr.isChecked()
            config['save_config'] = self.save_config.isChecked()
            config['strategy'] = self.strategy.currentText()
            config['timeframe'] = self.timeframe.currentText()
            self.saveConfig(config)

        #send params to main program to run on terminal
        if all(validation_list):
            command:str = f"""
                start /B start cmd /k {TO_RUN} \
                {params['login'][0]} \
                {params['password'][0]} \
                {params['server'][0]} \
                --use_atr={int(self.use_atr.isChecked())} \
                --unit_pip={(params['unit_pip'][0])} \
                --default_sl={params['default_sl'][0]} \
                --max_sl_dist={params['max_sl_dist'][0]} \
                --sl_trail={params['sl_trail'][0]} \
                --volume={params['volume'][0]} \
                --deviation={params['deviation'][0]} \
                --strategy={self.strategy.currentText()} \
                --symbol={params['symbol'][0]} \
                --default_tp={params['default_tp'][0]} \
                --timeframe={self.timeframe.currentText()} \
                --sr_likelihood={params['sr_likelihood'][0]} \
                --sr_threshold={params['sr_threshold'][0]} \
                --period={params['period'][0]} \
            """
            os.system(command)

        
if __name__ == '__main__':
    app = QApplication(sys.argv)

    bot_app = BotApplication()
    bot_app.show()
    sys.exit(app.exec())