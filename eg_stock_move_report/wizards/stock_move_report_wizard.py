from odoo import fields, models, api
import xlwt
import io
import xlsxwriter
import base64
from io import BytesIO
from datetime import datetime


class StockMoveReportWizard(models.TransientModel):
    _name = "stock.move.report.wizard"
    _description = "Stock Move Report"

    category_id = fields.Many2one('product.category', string='Product Category')
    location_id = fields.Many2one('stock.location', string='Location')
    from_date = fields.Date(string="Start Date", required=True)
    to_date = fields.Date(string="End Date", required=True)
    status = fields.Selection(selection=[("all", "All"), ("stock", "Available"), ("done", "Done")], string="Status")
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    usage = fields.Selection(
        selection=[("supplier", "Vendor Location"), ("view", "View"), ("internal", "Internal Location"),
                   ("customer", "Customer Location"), ("inventory", "Inventory Loss"), ("production", "Production"),
                   ("transit", "Transit Location")], string="Status")
    excel_report_data = fields.Binary(string="Data")
    all_location = fields.Many2many('stock.location', 'eg_report_stock_location_rel', 'eg_report_stock_id',
                                    'location_id', 'All locations')
    selected_locations = fields.Many2many('stock.location', string='Selected Locations')
    select_all = fields.Boolean(string='All Locations ')
    selection = fields.Selection([
        ('product', 'One One Product'),
        ('all', 'On All Products'),
        ('category', 'On Product Category'),
        ('brand', 'On Product Brand'),
    ], string='Product Filters', default='product', widget='radio')
    move_balance = fields.Float(string='Move Balance', compute='_compute_move_balance')
    all_locations = fields.Boolean(string='All Locations')
    stock_moves = fields.Many2many('stock.move', string='Stock Moves', compute='_compute_stock_moves')

    @api.depends('all_locations', 'selected_locations')
    def _compute_stock_moves(self):
        for wizard in self:
            if wizard.all_locations:
                stock_moves = self.env['stock.move'].search([])
            else:
                stock_moves = self.env['stock.move'].search([('location_id', 'in', wizard.selected_locations.ids)])
            wizard.stock_moves = stock_moves

    @api.depends('selected_locations', 'from_date', 'to_date')
    def _compute_move_balance(self):
        for wizard in self:
            product_moves = self.env['stock.move'].search([
                ('product_id', '=', wizard.product_id.id),
                ('location_id', 'in', wizard.selected_locations.ids),
                ('create_date', '>=', wizard.from_date),
                ('create_date', '<=', wizard.to_date),
                ('state', '=', 'done')
            ])

            move_in = sum(
                product_moves.filtered(lambda m: m.location_dest_id in wizard.selected_locations).mapped('product_qty'))
            move_out = sum(
                product_moves.filtered(lambda m: m.location_id in wizard.selected_locations).mapped('product_qty'))

            # Calculate opening balance
            opening_balance = wizard.calculate_opening_balance(product_moves)

            # Calculate move balance
            move_balance = opening_balance + move_in - move_out
            wizard.move_balance = move_balance

    def calculate_opening_balance(self, product_moves):
        opening_balance = sum(product_moves.mapped('product_qty'))
        return opening_balance

    @api.onchange('select_all')
    def _onchange_select_all(self):
        if self.select_all:
            all_locations = self.env['stock.location'].search([])
            self.all_location = fields.Many2many('stock.location')
        else:
            self.all_location = [(5,)]

    def action_generate_report(self):
        column = 0
        row = 0
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet("Product {}".format(self.product_id.name))
        fnames = ["Date", "Product", "Customer", "Brand", "Reference", "From", "To", "Move Qty", "Moving Balance"]
        header1 = xlwt.easyxf(
            "font: bold on, height 200;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        header2 = xlwt.easyxf(
            "font: bold on, height 200;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour white; alignment: horiz center ,vert center ")
        # worksheet.col(0).width = 5500
        # worksheet.col(1).width = 3100
        # worksheet.col(2).width = 5500
        # if partner_id.portal_marketplace:
        #     worksheet.col(2).width = 5500
        #     worksheet.col(3).width = 6000
        #     worksheet.col(4).width = 5500
        worksheet.write_merge(row, row, column, len(fnames) - 1, "Product Move Report", header1)
        row += 1
        row += 1
        worksheet.write_merge(row, row, 0, 1, "Date", header1)
        worksheet.write_merge(row, row, 2, 5, self.from_date.strftime("%Y-%m-%d"))
        worksheet.write_merge(row, row, 6, 8, self.to_date.strftime("%Y-%m-%d"))
        row += 1
        row += 1
        for header_name in fnames:
            worksheet.write(row, column, header_name, header1)
            column += 1
        row += 1
        move_condition = [("create_date", ">=", self.from_date),
                          ("create_date", "<=", self.to_date),
                          ('state', '=', 'done')
                          ]
        if self.selection:
            if self.selection == "product" and self.product_id:
                move_condition.append(('product_id', '=', self.product_id.id))
            elif self.selection == "category" and self.category_id:
                products = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
                move_condition.append(('product_id.categ_id', 'in', products.ids))

            elif self.all_locations == self.all_locations:
                move_condition.append(('location_id', 'in', self.stock_moves.ids))
                #location_id = self.env['stock.move'].search([])
                #move_condition.append(('location_id', '=', location_id.id))
        else:
            move_condition.append(('location_id', '!=', False))
        if self.location_id:
            move_condition.append(("location_id", "=", self.location_id.id))
        move_ids = self.env["stock.move"].search(move_condition)

        for move_id in move_ids:
            worksheet.write(row, 0, str(move_id.create_date.date()))
            worksheet.write(row, 1, move_id.product_id.name)
            worksheet.write(row, 2, move_id.picking_id.partner_id.name)
            worksheet.write(row, 4, move_id.origin if move_id.origin else "")
            worksheet.write(row, 5, move_id.location_id.display_name)
            worksheet.write(row, 6, move_id.location_dest_id.display_name)
            worksheet.write(row, 7, move_id.product_uom_qty)
            #worksheet.write(row, 8, dict(move_id._fields["state"].selection).get(move_id.state))
           # opening_balance = sum(move_id.mapped('product_qty'))
           # worksheet.write(row, 8, ((move_id.product_uom_qty + move_id.product_qty) - move_id.product_uom_qty))
            # Calculate product move balance
            product_moves = self.env['stock.move'].search([
                ('product_id', '=', move_id.product_id.id),
                ('create_date', '<=', move_id.create_date),
                ('state', '=', 'done')
            ])
            product_balance = (sum(product_moves.filtered(lambda m: m.location_dest_id == move_id.location_id).mapped(
                'product_qty')) - sum(
                product_moves.filtered(lambda m: m.location_id == move_id.location_dest_id).mapped('product_qty')) +
                               sum(product_moves.mapped('product_qty')))
            #opening_balance = sum(product_moves.mapped('product_qty'))
            # Write move balance
            worksheet.write(row, 8, product_balance)

            row += 1

        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        file_new = base64.encodebytes(fp.read())
        fp.close()
        self.write({"excel_report_data": file_new})
        return {
            "type": "ir.actions.act_url",
            "url": "web/content/?model=stock.move.report.wizard&download=true&field=excel_report_data&id={}&filename={}_stock_move_report - {}.xls".format(
                self.id, self.display_name, datetime.now().strftime("%Y-%m-%d")),
            "target": "self"
        }

