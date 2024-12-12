# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    over_credit_limit = fields.Boolean(compute="_compute_over_credit_limit", string="Over Credit Limit",
                                       search="_over_credit_limit_search",
                                       groups="account.group_account_invoice,account.group_account_readonly")

    @api.depends_context("company")
    def _compute_over_credit_limit(self):
        for partner in self:
            partner.over_credit_limit = (partner.credit > partner.credit_limit)

    @api.model
    def _over_credit_limit_search(self, operator, operand):
        self._cr.execute(f'''
            SELECT aml.partner_id
              FROM res_partner partner
         LEFT JOIN account_move_line aml ON aml.partner_id = partner.id
              JOIN account_move move ON move.id = aml.move_id
              JOIN res_company line_company ON line_company.id = aml.company_id
              JOIN ir_property credit_limit ON credit_limit.res_id = 'res.partner,' || partner.id 
                   AND credit_limit.name = 'credit_limit'
        RIGHT JOIN account_account acc ON aml.account_id = acc.id
             WHERE acc.account_type = 'asset_receivable'
               AND NOT acc.deprecated
               AND SPLIT_PART(line_company.parent_path, '/', 1)::int = {self.env.company.root_id.id}
               AND move.state = 'posted'
          GROUP BY aml.partner_id,credit_limit.value_float
            HAVING COALESCE(SUM(aml.amount_residual), 0) > credit_limit.value_float''')

        res = self._cr.fetchall()

        if not res:
            return [('id', '=', '0')]
        return [('id', 'in', [r[0] for r in res])]
