from dateutil.relativedelta import relativedelta

from odoo import fields, api, models
from odoo.exceptions import ValidationError
from datetime import datetime


class BorrowBook(models.Model):
    _name = "book.borrow"
    _inherit = ['book.info', 'mail.thread']
    book_info_id = fields.Many2one('book.info', string="Book Info ID")
    name = fields.Many2one('hr.employee', string="Tên sinh viên")
    name_of_book = fields.Char(string="Các cuốn sách mượn")
    name_of_leader = fields.Many2one('hr.employee', string="Người quản lý")
    date_borrow_book = fields.Date(string="Ngày mượn sách", )
    is_expried_of_book = fields.Integer(string='Thời hạn trả sách')
    date_return_expried = fields.Date(string="Hạn trả", compute='compute_deadline')
    number_of_money = fields.Integer(string='Hệ số trả mượn')
    email = fields.Char(string="Email")
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Waiting Confirm'),
                              ('approved', 'Approved')], string='Status', default='draft', index=True)

    @api.onchange("book_info_id")
    def check_borrow_book(self):
        self.name_of_book = self.book_info_id.name_of_book
        self.is_expried_of_book = self.book_info_id.is_expried_of_book
        self.number_of_money = self.book_info_id.number_of_money

    @api.depends("date_borrow_book", 'is_expried_of_book')
    def compute_deadline(self):
        for re in self:
            if re.date_borrow_book and re.is_expried_of_book:
                re.date_return_expried = re.date_borrow_book + relativedelta(months=re.book_info_id.is_expried_of_book)

    @api.one
    def started_progressbar(self):
        if self.state == "draft":
            self.write({'state': 'confirm'})
            mail_template = self.env.ref('mybook.mail_templates')
            mail_template.send_mail(self.id, force_send=True)

    @api.one
    def confirm_progressbar(self):
        if self.state == "confirm":
            self.write({'state': 'approved'})
            mail_template = self.env.ref('mybook.mail_borrow_accept')
            mail_template.send_mail(self.id, force_send=True)

    @api.constrains('name_of_book')
    def _check_name(self):
        partner_rec = self.env['book.borrow'].search(
            [('name_of_book', '=', self.name_of_book), ('id', '!=', self.id)])
        if partner_rec:
            raise ValidationError('! Sách này đã được mượn, vui lòng chọn quyển khác !')
