from odoo import fields, api, models
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ReturnBook(models.Model):
    _name = "book.return"

    book_borrow_id = fields.Many2one('book.borrow', string="Book borrow ID")
    name = fields.Many2one('hr.employee', string="Tên sinh viên")
    name_of_leader = fields.Many2one('hr.employee', string="Người quản lý")
    name_of_book = fields.Char(string="Các cuốn sách mượn")
    date_borrow_book = fields.Date(string="Ngày trả sách", )
    is_expried_of_book = fields.Date(string='Thời hạn trả sách')
    date_return_expried = fields.Date(string="Hạn trả")
    number_of_money = fields.Integer(string='Hệ số trả mượn')
    total_days = fields.Integer(string='Số ngày quá hạn', compute='computee_date')

    total_price = fields.Integer(string="Tổng tiền trả muộn", compute='compute_total_price')
    email = fields.Char(string="Email")

    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Waiting Confirm'),
                              ('approved', 'Approved')], string='Status', default='draft', index=True)

    @api.onchange("book_borrow_id")
    def show_list(self):
        self.name = self.book_borrow_id.name
        self.name_of_leader = self.book_borrow_id.name_of_leader
        self.date_borrow_book = self.book_borrow_id.date_borrow_book
        self.name_of_book = self.book_borrow_id.name_of_book
        self.date_return_expried = self.book_borrow_id.date_return_expried
        self.number_of_money = self.book_borrow_id.number_of_money

    @api.depends('date_return_expried', 'date_borrow_book', 'total_days')
    def computee_date(self):
        for r in self:
            if r.date_return_expried and r.date_borrow_book:
                d1 = datetime.strptime(str(r.date_return_expried), '%Y-%m-%d')
                d2 = datetime.strptime(str(r.date_borrow_book), '%Y-%m-%d')
                d3 = d1 - d2
                r.total_days = str(d3.days)

    @api.depends('number_of_money', 'total_days')
    def compute_total_price(self):
        for re in self:
            if re.number_of_money and re.total_days:
                re.total_price = re.total_days * re.number_of_money

    @api.one
    def started_progressbar(self):
        if self.state == "draft":
            self.write({'state': 'confirm'})
            mail_template = self.env.ref('mybook.mail_book_return')
            mail_template.send_mail(self.id, force_send=True)

    @api.one
    def confirm_progressbar(self):
        if self.state == "confirm":
            self.write({'state': 'approved'})
            mail_template = self.env.ref('mybook.mail_book_return_accept')
            mail_template.send_mail(self.id, force_send=True)

    @api.constrains('name_of_book')
    def _check_name(self):
        partner_rec = self.env['book.return'].search(
            [('name_of_book', '=', self.name_of_book), ('id', '!=', self.id)])
        if partner_rec:
            raise ValidationError('! Sách này chưa được trả, vui lòng lựa chọn khác !')
