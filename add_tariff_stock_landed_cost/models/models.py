# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, tools
from odoo.addons import decimal_precision as dp

class InheritStockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'


    @api.multi
    def compute_landed_cost(self):
        AdjustementLines = self.env['stock.valuation.adjustment.lines']
        AdjustementLines.search([('cost_id', 'in', self.ids)]).unlink()

        digits = dp.get_precision('Product Price')(self._cr)
        towrite_dict = {}
        for cost in self.filtered(lambda cost: cost.picking_ids):
            total_qty = 0.0
            total_cost = 0.0
            total_weight = 0.0
            total_volume = 0.0
            total_arancel = 0.0
            total_line = 0.0
            total_arancel = 0.0
            all_val_line_values = cost.get_valuation_lines()
            for val_line_values in all_val_line_values:
                for cost_line in cost.cost_lines:
                    val_line_values.update({'cost_id': cost.id, 'cost_line_id': cost_line.id})
                    self.env['stock.valuation.adjustment.lines'].create(val_line_values)
                total_qty += val_line_values.get('quantity', 0.0)
                total_weight += val_line_values.get('weight', 0.0)
                total_volume += val_line_values.get('volume', 0.0)

                former_cost = val_line_values.get('former_cost', 0.0)
                # round this because former_cost on the valuation lines is also rounded
                total_cost += tools.float_round(former_cost, precision_digits=digits[1]) if digits else former_cost

                total_line += 1

            for line in cost.cost_lines:
                value_split = 0.0
                for valuation in cost.valuation_adjustment_lines:
                    value = 0.0
                    if valuation.cost_line_id and valuation.cost_line_id.id == line.id:
                        if line.split_method == 'by_quantity' and total_qty:
                            per_unit = (line.price_unit / total_qty)
                            value = valuation.quantity * per_unit
                        elif line.split_method == 'by_weight' and total_weight:
                            per_unit = (line.price_unit / total_weight)
                            value = valuation.weight * per_unit
                        elif line.split_method == 'by_volume' and total_volume:
                            per_unit = (line.price_unit / total_volume)
                            value = valuation.volume * per_unit
                        elif line.split_method == 'equal':
                            value = (line.price_unit / total_line)
                        elif line.split_method == 'by_current_cost_price' and total_cost:
                            per_unit = (line.price_unit / total_cost)
                            value = valuation.former_cost * per_unit
                        elif line.split_method == 'arancel':
                            value = 0
                            print("Producto: ",line)
                        else:
                            value = (line.price_unit / total_line)

                        if digits:
                            value = tools.float_round(value, precision_digits=digits[1], rounding_method='UP')
                            fnc = min if line.price_unit > 0 else max
                            value = fnc(value, line.price_unit - value_split)
                            value_split += value

                        if valuation.id not in towrite_dict:
                            towrite_dict[valuation.id] = value
                        else:
                            towrite_dict[valuation.id] += value
        print("Pruebas: ",towrite_dict.items())
        for key, value in towrite_dict.items():
            AdjustementLines.browse(key).write({'additional_landed_cost': value})
        for x in AdjustementLines.search([('cost_id', 'in', self.ids)]):
        	if x.cost_line_id.product_id.split_method == 'arancel':
        		x.cost_line_id.price_unit = 0.0
        for x in AdjustementLines.search([('cost_id', 'in', self.ids)]):
        	if x.cost_line_id.product_id.split_method == 'arancel':
        		print("Lines: ", x.product_id.name, x.cost_line_id.id)
        		x.write({'additional_landed_cost': (x.former_cost_per_unit * (x.product_id.arancel_percent/100)) * x.quantity})
        		x.cost_line_id.price_unit += (x.former_cost_per_unit * (x.product_id.arancel_percent/100)) * x.quantity

        return True

class InheritStockLandedCostLines(models.Model):
    _inherit = 'stock.landed.cost.lines'

    split_method = fields.Selection(selection_add=[('arancel','Arancel')])


class InheritProductTemplate(models.Model):
    _inherit = 'product.template'

    split_method = fields.Selection(selection_add=[('arancel','Arancel')])
    arancel_percent = fields.Integer(
        string='Porcentaje para arancel',
        track_visibility='always',
        default= 0.0,
        help="Porcentaje para calcular el arancel en gastos de envio tomando el precio de venta para el calculo"
    )