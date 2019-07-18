# -*- coding: utf-8 -*-
from odoo import http

# class AddTariffStockLandedCost(http.Controller):
#     @http.route('/add_tariff_stock_landed_cost/add_tariff_stock_landed_cost/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_tariff_stock_landed_cost/add_tariff_stock_landed_cost/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_tariff_stock_landed_cost.listing', {
#             'root': '/add_tariff_stock_landed_cost/add_tariff_stock_landed_cost',
#             'objects': http.request.env['add_tariff_stock_landed_cost.add_tariff_stock_landed_cost'].search([]),
#         })

#     @http.route('/add_tariff_stock_landed_cost/add_tariff_stock_landed_cost/objects/<model("add_tariff_stock_landed_cost.add_tariff_stock_landed_cost"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_tariff_stock_landed_cost.object', {
#             'object': obj
#         })