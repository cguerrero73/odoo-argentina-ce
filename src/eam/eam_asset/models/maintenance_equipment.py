from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    asset_code = fields.Char(
        string="Equipment Code",
        required=True,
        copy=False,
        index=True,
        tracking=True,
        default=lambda self: self.env["ir.sequence"].next_by_code(
            "eam.maintenance.equipment"
        ),
        help="Business identifier of the equipment. It can only be set during creation.",
    )

    _asset_code_company_unique = models.Constraint(
        "unique(company_id, asset_code)",
        "The equipment code must be unique within the company.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            code = vals.get("asset_code") or self.env["ir.sequence"].next_by_code(
                "eam.maintenance.equipment"
            )
            if not code:
                raise ValidationError(_("The Equipment Code is required."))
            code = code.strip().upper()
            if not code:
                raise ValidationError(_("The Equipment Code cannot be empty."))
            vals["asset_code"] = code
        return super().create(vals_list)

    def write(self, vals):
        if "asset_code" in vals:
            new_code = (vals["asset_code"] or "").strip().upper()
            if any(record.asset_code != new_code for record in self):
                raise UserError(_("The Equipment Code cannot be changed after creation."))
            vals = dict(vals, asset_code=new_code)
        return super().write(vals)
