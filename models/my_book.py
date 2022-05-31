from odoo import fields, api, models


class BookInfo(models.Model):
    _name = "book.info"
    _rec_name = 'name_of_book'  # lấy tên theo record

    name_of_book = fields.Char(string="Tên sách")
    is_expried_of_book = fields.Integer(string="Thời hạn trả sách", default=2)
    number_of_money = fields.Float(string="Hệ số tính tiền trả muộn", default=5000)
