from datetime import datetime

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare, float_round
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    @api.multi
    def write(self, vals):
        for rec in self:
            if vals.get('state') and vals.get('state') == 'open' and rec.type == 'out_invoice':
                self.create_quant()
            if vals.get('state') and vals.get('state') == 'paid' and rec.type == 'out_refund':
                self.refund_quant()
            if vals.get('state') and vals.get('state') == 'paid' and rec.type == 'in_refund':
                self.reduce_quant_vendor()
            if vals.get('state') and vals.get('state') == 'open' and rec.type == 'in_invoice':
                self.add_quant_vendor()
        res = super(AccountInvoice, self).write(vals)
        return res




    @api.one
    def create_quant(self):
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        move_lines_list = []
        picking_type_id = self.env['stock.picking.type'].search([('code', '=', 'outgoing')])
        if picking_type_id:
            picking_type_id = picking_type_id[0]
        location_dest_id = self.env['stock.location'].search([('usage', '=', 'customer')])
        if location_dest_id:
            location_dest_id = location_dest_id[0]
        for inv_line in self.invoice_line_ids:
            line_val = {
                'product_id' : inv_line.product_id.id,
                'product_uom_qty':inv_line.quantity or False,
                'product_uom':inv_line.uom_id.id or False,
                'name' : self.number or '',
                'location_id':self.env.ref('stock.stock_location_stock').id or False,
                }
            line_tuple = (0,0,line_val)
            move_lines_list.append(line_tuple)
            location_id = inv_line.product_id.property_stock_inventory
        picking_val = {
            'partner_id' : self.partner_id.id,
            'origin' : self.number or '',
            'move_lines':move_lines_list,
            'picking_type_id':picking_type_id.id,
            'move_type':'one',
            'location_id':self.env.ref('stock.stock_location_stock').id or False,
            'location_dest_id' : location_dest_id.id or False,
            }
        picking_id = picking_obj.create(picking_val)
        print 'picking_id................',picking_id
        picking_id.action_confirm()
        for operation in picking_id.pack_operation_product_ids:
            quantity = [data.quantity for data in self.invoice_line_ids if data.product_id == operation.product_id]
#             if lot_id:
#             operation.pack_lot_ids = [(0, 0,  {'lot_id': lot_id[0].id})]
            operation.write({'qty_done': quantity[0]})
#         picking_id.action_assign()
        picking_id.force_assign()
        for operation in picking_id.pack_operation_product_ids:
            for ll in operation.pack_lot_ids:
                ll.unlink()
        for operation in picking_id.pack_operation_product_ids:
            quantity = [data.quantity for data in self.invoice_line_ids if data.product_id == operation.product_id]
#             lot_id = [data.lot_id for data in self.invoice_line_ids if data.product_id == operation.product_id]
#             if quantity:
#                 operation.pack_lot_ids = [(0, 0,  {'lot_id': lot_id[0].id})]
            operation.write({'qty_done': quantity[0]})
#         picking_id.action_confirm()
        picking_id.do_new_transfer()
        

    @api.one
    def refund_quant(self):
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        move_lines_list = []
        picking_type_id = self.env['stock.picking.type'].search([('code', '=', 'incoming')])
        if picking_type_id:
            picking_type_id = picking_type_id[0]
        location_dest_id = self.env['stock.location'].search([('usage', '=', 'customer')])
        if location_dest_id:
            location_dest_id = location_dest_id[0]
        for inv_line in self.invoice_line_ids:
            line_val = {
                'product_id' : inv_line.product_id.id,
                'product_uom_qty':inv_line.quantity or False,
                'product_uom':inv_line.uom_id.id or False,
                'name' : self.number or '',
#                 'location_id':self.env.ref('stock.stock_location_stock').id or False,
                'location_id':location_dest_id.id or False,
                }
            line_tuple = (0,0,line_val)
            move_lines_list.append(line_tuple)
            location_id = inv_line.product_id.property_stock_inventory
        picking_val = {
            'partner_id' : self.partner_id.id,
            'origin' : self.number or '',
            'move_lines':move_lines_list,
            'picking_type_id':picking_type_id.id,
            'move_type':'one',
            'location_id':location_dest_id.id or False,
            'location_dest_id' : self.env.ref('stock.stock_location_stock').id or False,
            }
        picking_id = picking_obj.create(picking_val)
        picking_id.action_confirm()
        for operation in picking_id.pack_operation_product_ids:
            quantity = [data.quantity for data in self.invoice_line_ids if data.product_id == operation.product_id]
#             if lot_id:
#             operation.pack_lot_ids = [(0, 0,  {'lot_id': lot_id[0].id})]
            operation.write({'qty_done': quantity[0]})
#         picking_id.action_assign()
        picking_id.force_assign()
        for operation in picking_id.pack_operation_product_ids:
            for ll in operation.pack_lot_ids:
                ll.unlink()
        for operation in picking_id.pack_operation_product_ids:
            quantity = [data.quantity for data in self.invoice_line_ids if data.product_id == operation.product_id]
#             lot_id = [data.lot_id for data in self.invoice_line_ids if data.product_id == operation.product_id]
#             if quantity:
#                 operation.pack_lot_ids = [(0, 0,  {'lot_id': lot_id[0].id})]
            operation.write({'qty_done': quantity[0]})
#         picking_id.action_confirm()
        picking_id.do_new_transfer()


    @api.one
    def reduce_quant_vendor(self):
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        move_lines_list = []
        picking_type_id = self.env['stock.picking.type'].search([('code', '=', 'outgoing')])
        if picking_type_id:
            picking_type_id = picking_type_id[0]
#         location_dest_id = self.env['stock.location'].search([('usage', '=', 'customer')])
        location_dest_id = self.env.ref('stock.stock_location_suppliers')
#         if location_dest_id:
#             location_dest_id = location_dest_id[0]
        for inv_line in self.invoice_line_ids:
            line_val = {
                'product_id' : inv_line.product_id.id,
                'product_uom_qty':inv_line.quantity or False,
                'product_uom':inv_line.uom_id.id or False,
                'name' : self.number or '',
                'location_id':self.env.ref('stock.stock_location_stock').id or False,
                }
            line_tuple = (0,0,line_val)
            move_lines_list.append(line_tuple)
            location_id = inv_line.product_id.property_stock_inventory
        picking_val = {
            'partner_id' : self.partner_id.id,
            'origin' : self.number or '',
            'move_lines':move_lines_list,
            'picking_type_id':picking_type_id.id,
            'move_type':'one',
            'location_id':self.env.ref('stock.stock_location_stock').id or False,
            'location_dest_id' : location_dest_id.id or False,
            }
        picking_id = picking_obj.create(picking_val)
        picking_id.action_confirm()
        for operation in picking_id.pack_operation_product_ids:
            quantity = [data.quantity for data in self.invoice_line_ids if data.product_id == operation.product_id]
#             if lot_id:
#             operation.pack_lot_ids = [(0, 0,  {'lot_id': lot_id[0].id})]
            operation.write({'qty_done': quantity[0]})
#         picking_id.action_assign()
        picking_id.force_assign()
        for operation in picking_id.pack_operation_product_ids:
            for ll in operation.pack_lot_ids:
                ll.unlink()
        for operation in picking_id.pack_operation_product_ids:
            quantity = [data.quantity for data in self.invoice_line_ids if data.product_id == operation.product_id]
#             lot_id = [data.lot_id for data in self.invoice_line_ids if data.product_id == operation.product_id]
#             if quantity:
#                 operation.pack_lot_ids = [(0, 0,  {'lot_id': lot_id[0].id})]
            operation.write({'qty_done': quantity[0]})
#         picking_id.action_confirm()
        picking_id.do_new_transfer()
        

    @api.one
    def add_quant_vendor(self):
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        move_lines_list = []
        picking_type_id = self.env['stock.picking.type'].search([('code', '=', 'incoming')])
        if picking_type_id:
            picking_type_id = picking_type_id[0]
        location_dest_id = self.env.ref('stock.stock_location_suppliers')
#         if location_dest_id:
#             location_dest_id = location_dest_id[0]
        for inv_line in self.invoice_line_ids:
            line_val = {
                'product_id' : inv_line.product_id.id,
                'product_uom_qty':inv_line.quantity or False,
                'product_uom':inv_line.uom_id.id or False,
                'name' : self.number or '',
#                 'location_id':self.env.ref('stock.stock_location_stock').id or False,
                'location_id':location_dest_id.id or False,
                }
            line_tuple = (0,0,line_val)
            move_lines_list.append(line_tuple)
            location_id = inv_line.product_id.property_stock_inventory
        picking_val = {
            'partner_id' : self.partner_id.id,
            'origin' : self.number or '',
            'move_lines':move_lines_list,
            'picking_type_id':picking_type_id.id,
            'move_type':'one',
            'location_id':location_dest_id.id or False,
            'location_dest_id' : self.env.ref('stock.stock_location_stock').id or False,
            }
        picking_id = picking_obj.create(picking_val)
        picking_id.action_confirm()
        for operation in picking_id.pack_operation_product_ids:
            quantity = [data.quantity for data in self.invoice_line_ids if data.product_id == operation.product_id]
#             if lot_id:
#             operation.pack_lot_ids = [(0, 0,  {'lot_id': lot_id[0].id})]
            operation.write({'qty_done': quantity[0]})
#         picking_id.action_assign()
        picking_id.force_assign()
        for operation in picking_id.pack_operation_product_ids:
            for ll in operation.pack_lot_ids:
                ll.unlink()
        for operation in picking_id.pack_operation_product_ids:
            quantity = [data.quantity for data in self.invoice_line_ids if data.product_id == operation.product_id]
#             lot_id = [data.lot_id for data in self.invoice_line_ids if data.product_id == operation.product_id]
#             if quantity:
#                 operation.pack_lot_ids = [(0, 0,  {'lot_id': lot_id[0].id})]
            operation.write({'qty_done': quantity[0]})
#         picking_id.action_confirm()
        picking_id.do_new_transfer()
# class AccountInvoiceLine(models.Model):
#     _inherit = "account.invoice.line"
#     
#     lot_id = fields.Many2one('stock.production.lot', string = 'Lot/Serial number')
# #     barcode = fields.Char(string = 'Barcode')
# 
#     @api.onchange('lot_id')
#     def onchange_lot_id(self):
#         if self.lot_id:
#             self.product_id = self.lot_id.product_id
#         else:
#             self.product_id = False
# 
#     @api.onchange('product_id')
#     def _onchange_product_id(self):
#         domain = {}
#         if not self.invoice_id:
#             return
# 
#         part = self.invoice_id.partner_id
#         fpos = self.invoice_id.fiscal_position_id
#         company = self.invoice_id.company_id
#         currency = self.invoice_id.currency_id
#         type = self.invoice_id.type
# 
#         if not part:
#             warning = {
#                     'title': _('Warning!'),
#                     'message': _('You must first select a partner!'),
#                 }
#             return {'warning': warning}
# 
#         if not self.product_id:
#             if type not in ('in_invoice', 'in_refund'):
#                 self.price_unit = 0.0
#             domain['uom_id'] = []
#             domain['lot_id'] = []
#         else:
#             lot_ids = self.env['stock.production.lot'].search([('product_id','=',self.product_id.id)]).ids
#             domain['lot_id'] = [('id', 'in', lot_ids)]
#             if part.lang:
#                 product = self.product_id.with_context(lang=part.lang)
#             else:
#                 product = self.product_id
# 
#             self.name = product.partner_ref
#             account = self.get_invoice_line_account(type, product, fpos, company)
#             if account:
#                 self.account_id = account.id
#             self._set_taxes()
# 
#             if type in ('in_invoice', 'in_refund'):
#                 if product.description_purchase:
#                     self.name += '\n' + product.description_purchase
#             else:
#                 if product.description_sale:
#                     self.name += '\n' + product.description_sale
# 
#             if not self.uom_id or product.uom_id.category_id.id != self.uom_id.category_id.id:
#                 self.uom_id = product.uom_id.id
#             domain['uom_id'] = [('category_id', '=', product.uom_id.category_id.id)]
# 
#             if company and currency:
#                 if company.currency_id != currency:
#                     self.price_unit = self.price_unit * currency.with_context(dict(self._context or {}, date=self.invoice_id.date_invoice)).rate
# 
#                 if self.uom_id and self.uom_id.id != product.uom_id.id:
#                     self.price_unit = product.uom_id._compute_price(self.price_unit, self.uom_id)
# 
#         return {'domain': domain}