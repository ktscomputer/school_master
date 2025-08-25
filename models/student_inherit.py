from odoo import models, fields, api
from datetime import datetime


class StudentMasterOne(models.Model):
    _inherit = 'student.master'

    total_fees_accumulated = fields.Float(
        string='Total Fees Accumulated',
        default=0.0,
        readonly=True
    )
    total_fees_receipted = fields.Float(
        string='Total Receipted Amount',
        default=0.0,
        readonly=True
    )
    academic_id = fields.Many2one(
        'student.academic',
        string='Academic Record',
        compute='_compute_academic_id',
        store=True
    )

    current_balance = fields.Float(
        string='Current Balance',
        related='academic_id.current_balance',
        store=True,
        readonly=True
    )


    last_fee_addition = fields.Datetime(
        string='Last Fee Addition',
        readonly=True
    )

    @api.depends('student_name')
    def _compute_academic_id(self):
        for student in self:
            academic_record = self.env['student.academic'].search([
                ('name', '=', student.id)
            ], limit=1)

            if not academic_record:
                # Create academic record if it doesn't exist
                academic_vals = {
                    'name': student.student_name,
                    'student_id': student.id,
                    'course': student.student_class_name.name if student.student_class_name else False,
                    'year': student.student_class.name if student.student_class else False,
                }
                academic_record = self.env['student.academic'].create(academic_vals)

            student.academic_id = academic_record.id


    """ 
    fee_history_ids = fields.One2many(
        'fee.addition.history',
        'student_id',
        string='Fee History'
    )
    receipt_ids = fields.One2many(
        'student.fee.receipt',
        'student_id',
        string='Payment Receipts'
    )

    @api.depends('total_fees_accumulated', 'total_fees_receipted')
    def _compute_current_balance(self):
        for student in self:
            student.current_balance = student.total_fees_accumulated - student.total_fees_receipted
    """

""" 
class StudentFee(models.Model):
    _inherit = 'student.academic'

    receipt_count = fields.Integer(
        string='Receipts Count',
        compute='_compute_receipt_count'
    )

    def _compute_receipt_count(self):
        for record in self:
            record.receipt_count = len(record.student_id.receipt_ids)

    def action_view_receipts(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment Receipts',
            'res_model': 'student.fee.receipt',
            'view_mode': 'tree,form',
            'domain': [('student_id', '=', self.student_id.id)],
            'context': {'default_student_id': self.student_id.id}
        }

    @api.model
    def _cron_add_fees_every_5min(self):
        # Enhanced cron job with history tracking
        fee_records = self.search([
            ('is_locked', '=', True),
            ('academic_fee', '>', 0)
        ])

        for fee in fee_records:
            student = fee.student_id
            if student:
                now = datetime.now()
                last_add = student.last_fee_addition or now
                minutes_passed = (now - last_add).total_seconds() / 60

                if minutes_passed >= 5:
                    intervals = int(minutes_passed // 5)
                    amount_to_add = fee.academic_fee * intervals

                    if amount_to_add > 0:
                        # Create history record
                        self.env['fee.addition.history'].create({
                            'student_id': student.id,
                            'amount': amount_to_add,
                            'addition_date': now,
                            'fee_record_id': fee.id
                        })

                        # Update student record
                        student.write({
                            'total_fees_accumulated': student.total_fees_accumulated + amount_to_add,
                            'last_fee_addition': now
                        })

"""