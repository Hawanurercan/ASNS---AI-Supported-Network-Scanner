import sys
import subprocess
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel, QLineEdit, QPushButton, \
    QTextEdit, QCheckBox, QComboBox, QFileDialog, QApplication
from PyQt5.QtCore import QThread, pyqtSignal
import google.generativeai as genai


class NmapScanThread(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, command):
        super(NmapScanThread, self).__init__()
        self.command = command

    def run(self):
        try:
            process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                    bufsize=1, universal_newlines=True)

            output_str = ""
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                line = line.rstrip()

                if 'tcp' in line and 'open' in line:
                    line_parts = line.split()
                    line_parts[0] = f'<font color="#DB9DFF">{line_parts[0]}</font>'
                    line_parts[-1] = f'<font color="#FAC146">{line_parts[-1]}</font>'
                    formatted_line = ' '.join(line_parts)
                    output_str += formatted_line + "\n"
                    self.update_signal.emit(formatted_line)
                else:
                    output_str += line + "\n"

            process.communicate()
            if process.returncode != 0:
                error_message = f"Process exited with error code: {process.returncode}"
                output_str += error_message + "\n"
                self.update_signal.emit(error_message)

            with open('output.txt', 'w') as output_file:
                output_file.write(output_str)



        except Exception as e:
            output_str = f'Error: {str(e)}'
            self.update_signal.emit(output_str)
            with open('output.txt', 'w') as output_file:
                output_file.write(output_str)


class NmapGUI(QMainWindow):
    def __init__(self):
        super(NmapGUI, self).__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('ASNS - AI Supported Network Scanner')
        self.setGeometry(100, 100, 1000, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        splitter = QSplitter(central_widget)
        layout.addWidget(splitter)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        splitter.addWidget(right_widget)

        self.setStyleSheet("background-color: #210405; color: white;")

        self.ip_label = QLabel('IP Addresses (comma-separated):')
        self.ip_label.setStyleSheet("color: white;")
        left_layout.addWidget(self.ip_label)

        self.ip_input = QLineEdit()
        self.ip_input.setStyleSheet("color: white; background-color: black;")
        left_layout.addWidget(self.ip_input)

        self.target_file_label = QLabel('Target File:')
        self.target_file_label.setStyleSheet("color: white;")
        left_layout.addWidget(self.target_file_label)

        self.target_file_input = QLineEdit()
        self.target_file_input.setStyleSheet("color: white; background-color: black;")
        left_layout.addWidget(self.target_file_input)

        self.browse_button = QPushButton('Browse')
        self.browse_button.setStyleSheet("color: white;")
        left_layout.addWidget(self.browse_button)
        self.browse_button.clicked.connect(self.browse_target_file)

        self.args_label = QLabel('Nmap Command Line Arguments:')
        self.args_label.setStyleSheet("color: white;")
        left_layout.addWidget(self.args_label)

        self.args_input = QLineEdit()
        self.args_input.setStyleSheet("color: white; background-color: black;")
        left_layout.addWidget(self.args_input)

        self.script_label = QLabel('Nmap Script:')
        self.script_label.setStyleSheet("color: white;")
        left_layout.addWidget(self.script_label)

        self.script_combo = QComboBox()
        self.script_combo.addItem('No Script')
        self.populate_script_combo()
        left_layout.addWidget(self.script_combo)

        self.args_group = QWidget()
        self.args_group.setLayout(QVBoxLayout())
        left_layout.addWidget(self.args_group)

        self.args_checkboxes = [
            ('-v', 'Verbose'),
            ('-p-', 'All Ports'),
            ('-sV', 'Service Version'),
            ('-sC', 'Script Scan'),
            ('-T4', 'Aggressive Timing'),
            ('-A', 'All-in-One'),
            ('-Pn', 'Skip Host Discovery'),
            ('-O', 'OS Detection'),
            ('-sU', 'UDP Scan')
        ]

        checkbox_layout = None
        for i, (arg, label) in enumerate(self.args_checkboxes):
            if i % 2 == 0:
                if checkbox_layout:
                    self.args_group.layout().addLayout(checkbox_layout)
                checkbox_layout = QHBoxLayout()

            checkbox = QCheckBox(label)
            checkbox.setStyleSheet("color: white; background-color: transparent; border: 2px solid black;")
            checkbox_layout.addWidget(checkbox)

        if checkbox_layout:
            self.args_group.layout().addLayout(checkbox_layout)

        self.scan_button = QPushButton('Run Nmap Scan')
        self.scan_button.setStyleSheet("color: white;")
        left_layout.addWidget(self.scan_button)
        self.scan_button.clicked.connect(self.run_nmap_scan)

        self.result_text = QTextEdit()
        self.result_text.setStyleSheet("background-color: black; color: white;")
        right_layout.addWidget(self.result_text)

        self.result2_text = QTextEdit()
        self.result2_text.setStyleSheet("background-color: black; color: white;")
        right_layout.addWidget(self.result2_text)

        self.thread = None

    def populate_script_combo(self):
        common_scripts = [
            'http-title',
            'ssl-heartbleed',
            'dns-zone-transfer',
            'ftp-anon',
            'smb-os-discovery',
            'banner',
            ''
        ]
        for script in common_scripts:
            self.script_combo.addItem(script)

    def browse_target_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Target File', '', 'Text Files (*.txt)', options=options)
        if file_path:
            self.target_file_input.setText(file_path)

    def run_nmap_scan(self):
        ip_addresses = self.ip_input.text().split(',')
        target_file = self.target_file_input.text()
        custom_args = self.args_input.text()

        if not ip_addresses and not target_file:
            self.result_text.setPlainText('Please provide IP addresses or a target file.')
            return

        command = ['nmap']

        if target_file:
            with open(target_file, 'r') as file:
                ip_addresses = [line.strip() for line in file if line.strip()]

        if ip_addresses:
            command.extend(ip_addresses)

        selected_args = [arg for arg, label in self.args_checkboxes if any(
            cb.text() == label for cb in self.args_group.findChildren(QCheckBox) if cb.isChecked())]
        command.extend(selected_args)

        if custom_args:
            command.extend(custom_args.split())

        self.scan_button.setEnabled(False)

        self.result_text.clear()

        self.thread = NmapScanThread(command)
        self.thread.update_signal.connect(self.update_result_text)
        self.thread.finished.connect(self.scan_finished)
        self.Ai()
        self.thread.start()

    def update_result_text(self, text):
        self.result_text.append(text)

    def scan_finished(self):
        self.scan_button.setEnabled(True)

    def Ai(self):
        try:
            genai.configure(api_key='AIzaSyA_8iHG9xFashfj9Kp0-wO1og_kEfPvpxs')
            generation_config = {
                "temperature": 0.9,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
            ]
            model = genai.GenerativeModel(model_name="gemini-pro")
            prompt_parts = ["penetration test report"]
            with open('output.txt', 'r') as output_file:
                veri = output_file.read()
            response = model.generate_content(veri + " write a penetration test report")
            response_text = response.text  # Varsayılan olarak bu özellik olmayabilir, bu nedenle uygun özelliği seçin
            self.result2_text.setPlainText(str(response_text))
        except Exception as e:
            self.result2_text.setPlainText(f"AI Error: {str(e)}")





def main():
    app = QApplication(sys.argv)
    window = NmapGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
