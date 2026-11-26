from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PySide6.QtWidgets import QFormLayout, QFrame, QComboBox, QLineEdit, QPushButton
from PySide6.QtWidgets import QCalendarWidget, QPlainTextEdit, QTableWidget, QHeaderView, QTableWidgetItem
from PySide6.QtWidgets import QAbstractItemView, QGroupBox, QGridLayout
from PySide6.QtCharts import QChart, QChartView, QAreaSeries, QLineSeries, QValueAxis, QScatterSeries
from PySide6.QtGui import QFont, QBrush, QColor, QPen
from PySide6.QtCore import Qt, QMargins
from trade_calculations import calculate_planned_r, calculate_realized_r
from trade_storage import load_trades, save_trades


def trade_result(realized_r):
    if realized_r > 0:
        return "Win"
    if realized_r < 0:
        return "Loss"
    return "Breakeven"


class TradingJournal(QWidget):
    def __init__(self):
        super().__init__()
        self.build_window()
        self.build_form()
        self.build_history()
        self.build_chart()
        self.build_performance()
        self.build_layout()
        self.load_history()

    def build_window(self):
        self.resize(1280, 720)
        self.setWindowTitle("t.r-journal-qt")
        self.setStyleSheet(
            "QWidget { background-color: black; color: #eeeeee; }"
            ' QLabel[panelHeading="true"] { font-size: 9pt; border: 1px solid #888888; padding: 3px 6px; }'
        )
        self.window_layout = QVBoxLayout(self)
        self.main_layout = QHBoxLayout()
        self.header_panel = QFrame(self)
        self.header_panel.setFrameShape(QFrame.Shape.Box)
        self.header_label = QLabel("t.r-journal-qt // sovva", self.header_panel)
        self.header_layout = QHBoxLayout(self.header_panel)
        self.header_layout.addWidget(self.header_label)
        self.window_layout.addWidget(self.header_panel)
        self.window_layout.addLayout(self.main_layout)

    def build_form(self):
        self.new_trade_panel = QFrame(self)
        self.new_trade_panel.setFrameShape(QFrame.Shape.Box)
        self.new_trade_label = QLabel("New Trade", self.new_trade_panel)
        self.new_trade_label.setProperty("panelHeading", True)
        self.new_trade_panel.setStyleSheet(
            'QLineEdit, QComboBox, QPlainTextEdit, QPushButton, QLabel[calculated="true"] { border: 1px solid #888888; }'
            ' QLineEdit, QComboBox, QLabel[calculated="true"] { min-height: 25px; }'
            ' QPushButton { padding: 4px 8px; }'
            ' QPushButton:hover { background-color: #252525; }'
            ' QPushButton:pressed { background-color: #3a3a3a; }'
            ' QLineEdit, QPlainTextEdit { placeholder-text-color: #eeeeee; }'
        )
        self.new_trade_layout = QVBoxLayout(self.new_trade_panel)
        self.new_trade_layout.setContentsMargins(8, 8, 8, 8)
        self.new_trade_layout.addWidget(self.new_trade_label)
        self.trade_form_layout = QFormLayout()
        self.trade_form_layout.setVerticalSpacing(15)
        self.date_row_layout = QHBoxLayout()
        self.trade_date_input = QLineEdit(self.new_trade_panel)
        self.trade_date_input.setPlaceholderText("yyyy-mm-dd")
        self.date_row_layout.addWidget(self.trade_date_input)
        self.calendar_button = QPushButton("Calendar", self.new_trade_panel)
        self.date_row_layout.addWidget(self.calendar_button)
        self.trade_form_layout.addRow("Date:", self.date_row_layout)
        self.trade_calendar = QCalendarWidget(self.new_trade_panel)
        self.trade_calendar.setWindowFlag(Qt.WindowType.Popup)
        self.trade_calendar.hide()
        self.calendar_button.clicked.connect(self.open_trade_calendar)
        self.trade_calendar.clicked.connect(self.select_trade_date)
        self.direction_input = QComboBox(self.new_trade_panel)
        self.direction_input.addItems(["Long", "Short"])
        self.direction_input.setPlaceholderText("--")
        self.direction_input.setCurrentIndex(-1)
        self.trade_form_layout.addRow("Direction:", self.direction_input)
        self.setup_input = QComboBox(self.new_trade_panel)
        self.setup_input.addItems(["nlc"])
        self.setup_input.setPlaceholderText("--")
        self.setup_input.setCurrentIndex(-1)
        self.trade_form_layout.addRow("Setup:", self.setup_input)
        self.entry_price_input = QLineEdit(self.new_trade_panel)
        self.entry_price_input.setPlaceholderText("--")
        self.trade_form_layout.addRow("Entry:", self.entry_price_input)
        self.stop_price_input = QLineEdit(self.new_trade_panel)
        self.stop_price_input.setPlaceholderText("--")
        self.trade_form_layout.addRow("Stop:", self.stop_price_input)
        self.target_price_input = QLineEdit(self.new_trade_panel)
        self.target_price_input.setPlaceholderText("--")
        self.trade_form_layout.addRow("Target:", self.target_price_input)
        self.exit_price_input = QLineEdit(self.new_trade_panel)
        self.exit_price_input.setPlaceholderText("--")
        self.trade_form_layout.addRow("Exit:", self.exit_price_input)
        self.planned_r_label = QLabel("--", self.new_trade_panel)
        self.planned_r_label.setProperty("calculated", True)
        self.trade_form_layout.addRow("Planned R:", self.planned_r_label)
        self.realized_r_label = QLabel("--", self.new_trade_panel)
        self.realized_r_label.setProperty("calculated", True)
        self.trade_form_layout.addRow("Realized R:", self.realized_r_label)
        self.result_label = QLabel("--", self.new_trade_panel)
        self.result_label.setProperty("calculated", True)
        self.trade_form_layout.addRow("Result:", self.result_label)
        self.entry_price_input.textChanged.connect(self.update_planned_r)
        self.stop_price_input.textChanged.connect(self.update_planned_r)
        self.target_price_input.textChanged.connect(self.update_planned_r)
        self.direction_input.currentTextChanged.connect(self.update_planned_r)
        self.entry_price_input.textChanged.connect(self.update_realized_r)
        self.stop_price_input.textChanged.connect(self.update_realized_r)
        self.exit_price_input.textChanged.connect(self.update_realized_r)
        self.direction_input.currentTextChanged.connect(self.update_realized_r)
        self.notes_input = QPlainTextEdit(self.new_trade_panel)
        self.line_height = self.notes_input.fontMetrics().lineSpacing()
        self.notes_padding = 2 * (int(self.notes_input.document().documentMargin()) + self.notes_input.frameWidth())
        self.notes_input.setFixedHeight(3 * self.line_height + self.notes_padding)
        self.trade_form_layout.addRow("Notes:", self.notes_input)
        self.new_trade_layout.addLayout(self.trade_form_layout)
        self.save_trade_button = QPushButton("Save Trade", self.new_trade_panel)
        self.new_trade_layout.addStretch()
        self.new_trade_layout.addSpacing(13)
        self.trade_action_layout = QHBoxLayout()
        self.trade_action_layout.addWidget(self.save_trade_button)
        self.new_trade_layout.addLayout(self.trade_action_layout)
        self.cancel_edit_button = QPushButton("Cancel", self.new_trade_panel)
        self.trade_action_layout.addWidget(self.cancel_edit_button)
        self.cancel_edit_button.hide()
        self.delete_trade_button = QPushButton("Delete Trade", self.new_trade_panel)
        self.new_trade_layout.addWidget(self.delete_trade_button)
        self.delete_trade_button.hide()
        self.delete_confirmation = QGroupBox("Confirm Delete", self.new_trade_panel)
        self.delete_confirmation_layout = QVBoxLayout(self.delete_confirmation)
        self.delete_confirmation_label = QLabel("", self.delete_confirmation)
        self.delete_confirmation_layout.addWidget(self.delete_confirmation_label)
        self.delete_choice_layout = QHBoxLayout()
        self.delete_confirmation_layout.addLayout(self.delete_choice_layout)
        self.keep_trade_button = QPushButton("Keep Trade", self.delete_confirmation)
        self.delete_choice_layout.addWidget(self.keep_trade_button)
        self.confirm_delete_button = QPushButton("Confirm Delete", self.delete_confirmation)
        self.delete_choice_layout.addWidget(self.confirm_delete_button)
        self.new_trade_layout.addWidget(self.delete_confirmation)
        self.delete_confirmation.hide()
        self.editing_trade_index = None
        self.editing_trade_record = None
        self.save_trade_button.clicked.connect(self.save_trade)
        self.cancel_edit_button.clicked.connect(self.reset_trade_form)
        self.delete_trade_button.clicked.connect(self.show_delete_confirmation)
        self.keep_trade_button.clicked.connect(self.hide_delete_confirmation)
        self.confirm_delete_button.clicked.connect(self.confirm_trade_delete)
        self.main_layout.addWidget(self.new_trade_panel, 1)

    def build_history(self):
        self.right_panel = QWidget(self)
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.trade_history_panel = QFrame(self.right_panel)
        self.trade_history_panel.setFrameShape(QFrame.Shape.Box)
        self.trade_history_label = QLabel("Trade History", self.trade_history_panel)
        self.trade_history_label.setProperty("panelHeading", True)
        self.trade_history_layout = QVBoxLayout(self.trade_history_panel)
        self.trade_history_layout.setContentsMargins(8, 8, 8, 8)
        self.trade_history_layout.addWidget(self.trade_history_label, 0, Qt.AlignmentFlag.AlignTop)
        self.trade_history_table = QTableWidget(self.trade_history_panel)
        self.trade_history_table.setShowGrid(False)
        self.trade_history_table.setStyleSheet("QTableWidget { outline: none; } "
            "QTableWidget::item { border-right: 1px solid #444444; } "
            "QTableWidget::item:selected { background-color: #252525; color: #eeeeee; border-top: 1px solid #888888; border-bottom: 1px solid #888888; }")
        self.trade_history_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section { background-color: #111111; border: 1px solid #666666; padding-left: 4px; }"
        )
        self.history_columns = [
            "#", "Date", "Dir", "Setup", "Entry", "Stop", "Target", "Exit", "Planned R", "Realized R", "Result", "Edit",
        ]
        self.trade_history_table.setColumnCount(len(self.history_columns))
        self.trade_history_table.setHorizontalHeaderLabels(self.history_columns)
        self.trade_history_table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.trade_history_table.verticalHeader().hide()
        self.trade_history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.trade_history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.trade_history_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.trade_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.trade_history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.trade_history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.trade_history_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
        self.trade_history_table.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)
        self.trade_history_layout.addWidget(self.trade_history_table)
        self.notes_group = QGroupBox("Selected Trade Notes:", self.trade_history_panel)
        self.notes_group_layout = QVBoxLayout(self.notes_group)
        self.selected_trade_notes = QPlainTextEdit(self.notes_group)
        self.selected_trade_notes.setReadOnly(True)
        self.selected_trade_notes.setFrameShape(QFrame.Shape.NoFrame)
        self.selected_trade_notes.setFixedHeight(3 * self.line_height + self.notes_padding)
        self.notes_group_layout.addWidget(self.selected_trade_notes)
        self.trade_history_layout.addWidget(self.notes_group)
        self.trade_history_table.itemSelectionChanged.connect(self.show_selected_trade_notes)

    def build_chart(self):
        self.overview_layout = QHBoxLayout()
        self.cumulative_r_panel = QFrame(self.right_panel)
        self.cumulative_r_panel.setFrameShape(QFrame.Shape.Box)
        self.cumulative_r_label = QLabel("Cumulative R", self.cumulative_r_panel)
        self.cumulative_r_label.setProperty("panelHeading", True)
        self.cumulative_r_layout = QVBoxLayout(self.cumulative_r_panel)
        self.cumulative_r_layout.setContentsMargins(8, 8, 8, 8)
        self.cumulative_r_layout.addWidget(self.cumulative_r_label, 0, Qt.AlignmentFlag.AlignTop)
        self.cumulative_chart = QChart()
        self.cumulative_r_series = QLineSeries()
        self.cumulative_r_area = QAreaSeries(self.cumulative_r_series)
        self.cumulative_chart.addSeries(self.cumulative_r_area)
        self.trade_dots = QScatterSeries()
        self.trade_rows_by_dot = {}
        self.cumulative_chart.addSeries(self.trade_dots)
        self.cumulative_chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        self.trade_dots.setMarkerSize(9)
        self.trade_dots.setColor(QColor("#888888"))
        self.trade_dots.setSelectedColor(QColor("#cccccc"))
        self.trade_dots.setBorderColor(QColor("transparent"))
        self.cumulative_chart.setBackgroundBrush(QBrush(QColor("#000000")))
        self.cumulative_r_area.setColor(QColor(48, 48, 48, 150))
        self.cumulative_r_area.setPen(QPen(QColor("#eeeeee")))
        self.cumulative_chart.legend().hide()
        self.cumulative_chart.setMargins(QMargins(0, 0, 0, 0))
        self.cumulative_chart_view = QChartView(self.cumulative_chart)
        self.cumulative_r_layout.addWidget(self.cumulative_chart_view)
        self.trade_dots.clicked.connect(self.select_trade_from_dot)
        self.trade_dots.hovered.connect(self.highlight_trade_dot)

    def build_performance(self):
        self.performance_panel = QFrame(self.right_panel)
        self.performance_panel.setFrameShape(QFrame.Shape.Box)
        self.performance_label = QLabel("Performance", self.performance_panel)
        self.performance_label.setProperty("panelHeading", True)
        self.performance_layout = QVBoxLayout(self.performance_panel)
        self.performance_layout.setContentsMargins(8, 8, 8, 8)
        self.performance_layout.addWidget(self.performance_label, 0, Qt.AlignmentFlag.AlignTop)
        self.performance_grid = QGridLayout()
        self.total_trades_label = QLabel("--", self.performance_panel)
        self.performance_grid.addWidget(QLabel("Total Trades:", self.performance_panel), 1, 0)
        self.performance_grid.addWidget(self.total_trades_label, 1, 1)
        self.wins_label = QLabel("--", self.performance_panel)
        self.performance_grid.addWidget(QLabel("Wins:", self.performance_panel), 3, 0)
        self.performance_grid.addWidget(self.wins_label, 3, 1)
        self.losses_label = QLabel("--", self.performance_panel)
        self.performance_grid.addWidget(QLabel("Losses:", self.performance_panel), 5, 0)
        self.performance_grid.addWidget(self.losses_label, 5, 1)
        self.win_rate_label = QLabel("--", self.performance_panel)
        self.performance_grid.addWidget(QLabel("Win Rate:", self.performance_panel), 7, 0)
        self.performance_grid.addWidget(self.win_rate_label, 7, 1)
        self.avg_win_r_label = QLabel("--", self.performance_panel)
        self.performance_grid.addWidget(QLabel("Avg R (Win):", self.performance_panel), 9, 0)
        self.performance_grid.addWidget(self.avg_win_r_label, 9, 1)
        self.avg_loss_r_label = QLabel("--", self.performance_panel)
        self.performance_grid.addWidget(QLabel("Avg R (Loss):", self.performance_panel), 11, 0)
        self.performance_grid.addWidget(self.avg_loss_r_label, 11, 1)
        self.expectancy_label = QLabel("--", self.performance_panel)
        self.performance_grid.addWidget(QLabel("Expectancy:", self.performance_panel), 13, 0)
        self.performance_grid.addWidget(self.expectancy_label, 13, 1)
        self.total_r_label = QLabel("--", self.performance_panel)
        self.performance_grid.addWidget(QLabel("Total R:", self.performance_panel), 15, 0)
        self.performance_grid.addWidget(self.total_r_label, 15, 1)
        self.max_drawdown_label = QLabel("--", self.performance_panel)
        self.performance_grid.addWidget(QLabel("Max Drawdown:", self.performance_panel), 17, 0)
        self.performance_grid.addWidget(self.max_drawdown_label, 17, 1)
        self.performance_grid.setVerticalSpacing(0)
        for gap_row in range(0, 19, 2):
            self.performance_grid.setRowStretch(gap_row, 1)
        self.performance_layout.addLayout(self.performance_grid, 1)

    def build_layout(self):
        self.overview_layout.addWidget(self.cumulative_r_panel, 2)
        self.overview_layout.addWidget(self.performance_panel, 1)
        self.right_layout.addLayout(self.overview_layout, 1)
        self.right_layout.addWidget(self.trade_history_panel, 1)
        self.main_layout.addWidget(self.right_panel, 3)

    def load_history(self):
        try:
            trades = load_trades()
            self.refresh_trade_history(trades)
            self.refresh_performance(trades)
        except (OSError, ValueError) as error:
            print(f"Could not load trade history: {error}")

    def open_trade_calendar(self):
        self.trade_calendar.move(self.trade_date_input.mapToGlobal(self.trade_date_input.rect().bottomLeft()))
        self.trade_calendar.show()

    def select_trade_date(self, date):
        self.trade_date_input.setText(date.toString("yyyy-MM-dd"))
        self.trade_calendar.hide()

    def update_planned_r(self):
        entry_text = self.entry_price_input.text()
        stop_text = self.stop_price_input.text()
        target_text = self.target_price_input.text()
        direction_text = self.direction_input.currentText()
        if "" in (entry_text, stop_text, target_text, direction_text):
            self.planned_r_label.setText("--")
            return
        try:
            entry = float(entry_text)
            stop = float(stop_text)
            target = float(target_text)
            planned_r = calculate_planned_r(entry, stop, target, direction_text)
        except ValueError:
            self.planned_r_label.setText("--")
            return
        self.planned_r_label.setText(f"{planned_r:.2f}R")

    def update_realized_r(self):
        entry_text = self.entry_price_input.text()
        stop_text = self.stop_price_input.text()
        exit_text = self.exit_price_input.text()
        direction_text = self.direction_input.currentText()
        if "" in (entry_text, stop_text, exit_text, direction_text):
            self.realized_r_label.setText("--")
            self.result_label.setText("--")
            return
        try:
            entry = float(entry_text)
            stop = float(stop_text)
            exit_price = float(exit_text)
            realized_r = calculate_realized_r(entry, stop, exit_price, direction_text)
        except ValueError:
            self.realized_r_label.setText("--")
            self.result_label.setText("--")
            return
        self.realized_r_label.setText(f"{realized_r:.2f}R")
        self.result_label.setText(trade_result(realized_r))

    def reset_trade_form(self):
        self.editing_trade_index = None
        self.editing_trade_record = None
        self.save_trade_button.setText("Save Trade")
        self.cancel_edit_button.hide()
        self.delete_trade_button.hide()
        self.delete_confirmation.hide()
        self.save_trade_button.show()
        self.trade_date_input.clear()
        self.entry_price_input.clear()
        self.stop_price_input.clear()
        self.target_price_input.clear()
        self.exit_price_input.clear()
        self.notes_input.clear()
        self.direction_input.setCurrentIndex(-1)
        self.setup_input.setCurrentIndex(-1)

    def save_trade(self):
        date_text = self.trade_date_input.text()
        direction_text = self.direction_input.currentText()
        setup_text = self.setup_input.currentText()
        entry_text = self.entry_price_input.text()
        stop_text = self.stop_price_input.text()
        target_text = self.target_price_input.text()
        exit_text = self.exit_price_input.text()
        notes_text = self.notes_input.toPlainText()
        if "" in (date_text, direction_text, setup_text, entry_text, stop_text, target_text, exit_text):
            print("Fill in all fields except Notes.")
            return
        try:
            entry = float(entry_text)
            stop = float(stop_text)
            target = float(target_text)
            exit_price = float(exit_text)
        except ValueError:
            print("Enter valid numbers for Entry, Stop, Target, and Exit")
            return
        try:
            planned_r = calculate_planned_r(entry, stop, target, direction_text)
            realized_r = calculate_realized_r(entry, stop, exit_price, direction_text)
        except ValueError as error:
            print(error)
            return
        result = trade_result(realized_r)

        trade = {
            "date": date_text,
            "direction": direction_text,
            "setup": setup_text,
            "entry": entry,
            "stop": stop,
            "target": target,
            "exit": exit_price,
            "planned_r": planned_r,
            "realized_r": realized_r,
            "result": result,
            "notes": notes_text
        }
        try:
            trades = load_trades()
            if self.editing_trade_index is None:
                trades.append(trade)
            else:
                if not 0 <= self.editing_trade_index < len(trades) or trades[self.editing_trade_index] != self.editing_trade_record:
                    raise ValueError("The saved trade has changed. Reopen Trade History and try again.")
                trades[self.editing_trade_index] = trade
            save_trades(trades)
        except (OSError, ValueError) as error:
            print(f"Could not save trade: {error}")
            return

        self.reset_trade_form()

        self.refresh_dashboard(trades)

    def show_delete_confirmation(self):
        self.save_trade_button.hide()
        self.cancel_edit_button.hide()
        self.delete_trade_button.hide()
        self.delete_confirmation.show()

    def hide_delete_confirmation(self):
        self.delete_confirmation.hide()
        self.save_trade_button.show()
        self.cancel_edit_button.show()
        self.delete_trade_button.show()

    def confirm_trade_delete(self):
        if self.editing_trade_index is None or not self.delete_confirmation.isVisible():
            return
        try:
            trades = load_trades()
        except (OSError, ValueError) as error:
            print(f"Could not load trades for deletion: {error}")
            return

        if not 0 <= self.editing_trade_index < len(trades) or trades[self.editing_trade_index] != self.editing_trade_record:
            print("The saved trade has changed. Reopen Trade History and try again.")
            return

        trades.pop(self.editing_trade_index)
        try:
            save_trades(trades)
        except (OSError, ValueError) as error:
            print(f"Could not delete trade: {error}")
            return

        self.reset_trade_form()
        self.refresh_dashboard(trades)

    def show_selected_trade_notes(self):
        selected_rows = self.trade_history_table.selectionModel().selectedRows()
        if not selected_rows:
            self.selected_trade_notes.setPlainText("--")
            return

        row_index = selected_rows[0].row()
        number_item = self.trade_history_table.item(row_index, 0)

        notes = number_item.data(Qt.ItemDataRole.UserRole)
        self.selected_trade_notes.setPlainText(notes or "--")

    def start_trade_edit(self, trade, saved_index):
        self.editing_trade_index = saved_index
        self.editing_trade_record = trade.copy()
        self.trade_date_input.setText(trade["date"])
        self.direction_input.setCurrentText(trade["direction"])
        self.setup_input.setCurrentText(trade["setup"])
        self.entry_price_input.setText(str(trade["entry"]))
        self.stop_price_input.setText(str(trade["stop"]))
        self.target_price_input.setText(str(trade["target"]))
        self.exit_price_input.setText(str(trade["exit"]))
        self.notes_input.setPlainText(trade.get("notes", ""))
        self.save_trade_button.setText("Save Changes")
        self.hide_delete_confirmation()
        self.delete_confirmation_label.setText(f"Delete {trade['date']} {trade['direction']} trade?")

    def refresh_trade_history(self, trades):
        self.trade_history_table.setRowCount(len(trades))
        for row_index, trade in enumerate(reversed(trades)):
            trade_number = len(trades) - row_index
            number_item = QTableWidgetItem(str(trade_number))
            number_item.setData(Qt.ItemDataRole.UserRole, trade.get("notes", ""))
            self.trade_history_table.setItem(row_index, 0, number_item)
            self.trade_history_table.setItem(row_index, 1, QTableWidgetItem(trade["date"]))
            self.trade_history_table.setItem(row_index, 2, QTableWidgetItem(trade["direction"]))
            self.trade_history_table.setItem(row_index, 3, QTableWidgetItem(trade["setup"]))

            entry_display = f"{trade['entry']:.2f}"
            self.trade_history_table.setItem(row_index, 4, QTableWidgetItem(entry_display))

            stop_display = f"{trade['stop']:.2f}"
            self.trade_history_table.setItem(row_index, 5, QTableWidgetItem(stop_display))

            target_display = f"{trade['target']:.2f}"
            self.trade_history_table.setItem(row_index, 6, QTableWidgetItem(target_display))

            exit_display = f"{trade['exit']:.2f}"
            self.trade_history_table.setItem(row_index, 7, QTableWidgetItem(exit_display))

            planned_r_display = f"{trade['planned_r']:.2f}R"
            self.trade_history_table.setItem(row_index, 8, QTableWidgetItem(planned_r_display))

            realized_r_display = f"{trade['realized_r']:.2f}R"
            self.trade_history_table.setItem(row_index, 9, QTableWidgetItem(realized_r_display))

            result_item = QTableWidgetItem(trade["result"])
            result_color = {"Win": "#72d98b", "Loss": "#ff7777"}.get(trade["result"], "#eeeeee")
            result_item.setForeground(QBrush(QColor(result_color)))

            self.trade_history_table.setItem(row_index, 10, result_item)

            edit_button = QPushButton("[Edit]", self.trade_history_table)
            edit_button.clicked.connect(
                lambda checked=False, record=trade, index=trade_number - 1: self.start_trade_edit(record, index)
            )
            self.trade_history_table.setCellWidget(row_index, 11, edit_button)

    def select_trade_from_dot(self, point):
        dot_number = int(point.x())
        self.trade_history_table.selectRow(self.trade_rows_by_dot[dot_number])

    def highlight_trade_dot(self, point, hovered):
        self.trade_dots.setPointSelected(int(point.x()) - 1, hovered)

    def refresh_performance(self, trades):
        self.total_trades_label.setText(str(len(trades)))
        wins = 0
        losses = 0
        total_r = 0.0
        win_r_total = 0.0
        loss_r_total = 0.0
        peak_r = 0.0
        max_drawdown = 0.0
        trades_by_date = sorted(enumerate(trades), key=lambda pair: pair[1]["date"])
        cumulative_r_values = [0.0]
        self.trade_rows_by_dot.clear()
        for saved_index, trade in trades_by_date:
            total_r += trade["realized_r"]
            cumulative_r_values.append(total_r)
            dot_number = len(cumulative_r_values) - 1
            self.trade_rows_by_dot[dot_number] = len(trades) - 1 - saved_index
            peak_r = max(peak_r, total_r)
            max_drawdown = min(max_drawdown, total_r - peak_r)
            if trade["result"] == "Win":
                wins += 1
                win_r_total += trade["realized_r"]
            elif trade["result"] == "Loss":
                losses += 1
                loss_r_total += trade["realized_r"]

        self.cumulative_r_series.clear()
        self.trade_dots.clear()
        for trade_index, running_r in enumerate(cumulative_r_values):
            self.cumulative_r_series.append(trade_index, running_r)
            if trade_index > 0:
                self.trade_dots.append(trade_index, running_r)

        chart_end = max(1, len(trades) + 0.5)
        self.cumulative_r_series.append(chart_end, cumulative_r_values[-1])
    
        self.cumulative_chart.createDefaultAxes()
        self.cumulative_chart.axes(Qt.Orientation.Horizontal)[0].setRange(0, chart_end)
        self.cumulative_chart.axes(Qt.Orientation.Horizontal)[0].setLabelsVisible(False)
        vertical_axis = self.cumulative_chart.axes(Qt.Orientation.Vertical)[0]
        vertical_axis.setRange(min(cumulative_r_values) - 0.5, max(cumulative_r_values) + 0.5)

        vertical_axis.setTickAnchor(0)

        vertical_axis.setTickInterval(1)
        vertical_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        vertical_axis.setLabelFormat("%.0fR  ")

        grid_pen = QPen(QBrush(QColor("#444444")), 1, Qt.PenStyle.DotLine)
        for axis in self.cumulative_chart.axes():
            axis.setGridLinePen(grid_pen)

        self.wins_label.setText(str(wins))
        self.losses_label.setText(str(losses))
        self.total_r_label.setText(f"{total_r:+.2f}R")
        self.max_drawdown_label.setText(f"{max_drawdown:.2f}R")

        if trades:
            self.win_rate_label.setText(f"{wins / len(trades):.1%}")
            self.expectancy_label.setText(f"{total_r / len(trades):+.2f}R")
        else:
            self.win_rate_label.setText("--")
            self.expectancy_label.setText("--")

        if wins:
            self.avg_win_r_label.setText(f"{win_r_total / wins:+.2f}R")
        else:
            self.avg_win_r_label.setText("--")

        if losses:
            self.avg_loss_r_label.setText(f"{loss_r_total / losses:+.2f}R")
        else:
            self.avg_loss_r_label.setText("--")

    def refresh_dashboard(self, trades):
        self.refresh_trade_history(trades)
        self.refresh_performance(trades)


def main():
    app = QApplication([])
    app.setFont(QFont("Consolas", 11))
    window = TradingJournal()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()