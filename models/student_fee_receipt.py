from odoo import models,fields,api
import logging
_logger = logging.getLogger(__name__)


class StudentFeeReceipt(models.Model):
    _name = 'student.fee.receipt'
    _description = 'Student Fee Receipts'
    _rec_name = 'student_id'

    name = fields.Char(
        string='Receipt Number',
        default=lambda self: self.env['ir.sequence'].next_by_code('student.fee.receipt'),
        readonly=True
    )
    student_id = fields.Many2one(
        'student.master',
        string='Student Name',
    )
    course = fields.Char(string='Course')
    amount = fields.Float(
        string='Amount',
        required=True
    )
    payment_date = fields.Datetime(
        string='Payment Date',
        default=fields.Datetime.now
    )
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('card', 'Credit/Debit Card'),
        ('online', 'Online Payment')
    ], string='Payment Method',default='cash' )
    reference = fields.Char(string='Payment Reference')
    collected_by = fields.Many2one(
        'res.users',
        string='Collected By',
        default=lambda self: self.env.user
    )


    is_locked = fields.Boolean(string='Locked', default=False)

    def action_save(self):
        self.write({'is_locked': True})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_edit(self):
        self.write({'is_locked': False})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.onchange('student_id')
    def _onchange_student_id(self):
        # When student is selected, auto-fill course from student.master
        for rec in self:
            if rec.student_id:
                rec.course = rec.student_id.student_class_name.name
            else:
                rec.course = False

    def action_run_fee_update(self):
        academic_students = self.env['student.academic'].search([])
        for academic in academic_students:
            if academic.academic_fee > 0:
                academic.write({
                    'total_fees_accumulated': academic.total_fees_accumulated + academic.academic_fee,
                    'last_fee_addition': fields.Datetime.now(),
                })
                _logger.info("Added academic fee for student %s", academic.student_id.student_name)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.model_create_multi
    def create(self, vals_list):

        # 1. Call the super method to create the records efficiently in one batch.
        records = super(StudentFeeReceipt, self).create(vals_list)

        # 2. Iterate over the newly created records to apply your custom logic.
        for rec in records:
            if rec.student_id:
                academic = self.env['student.academic'].search([
                    ('name', '=', rec.student_id.id),
                    ('active', '=', True)
                ], limit=1)

                if not academic:
                    # Fallback search by name if ID search fails
                    academic = self.env['student.academic'].search([
                        ('name', '=', rec.student_id.student_name),
                        ('active', '=', True)
                    ], limit=1)

                if academic:
                    academic.write({
                        'fee_receipt': academic.fee_receipt + rec.amount
                    })
        return records


class FeeUpdateWizard(models.TransientModel):
    _name = 'fee.update.wizard'
    _description = 'Fee Update Wizard'

    confirm = fields.Boolean(string="Confirm Fee Update?")
    can_execute = fields.Boolean(string="Can Execute", compute='_compute_can_execute', store=False)

    def action_add_academic_fee_all(self):
        academic_students = self.env['student.academic'].search([])
        updated_count = 0

        for academic in academic_students:
            # Get the course fee from student.class.name based on the course
            if academic.course:
                course = self.env['student.class.name'].search([('name', '=', academic.course)], limit=1)
                if course and course.quarter_fee > 0:
                    academic.write({
                        'total_fees_accumulated': academic.total_fees_accumulated + course.quarter_fee,
                        'last_fee_addition': fields.Datetime.now(),
                    })
                    updated_count += 1
                    _logger.info("Added fee %s for student %s (Course: %s)", course.quarter_fee, academic.name,
                                 academic.course)

        _logger.info("Academic fees updated for %s students", updated_count)
        return {'type': 'ir.actions.act_window_close'}

    @api.depends()
    def _compute_can_execute(self):
        last_execution = self.env['ir.config_parameter'].get_param('fee_update.last_execution')
        if last_execution:
            last_date = fields.Datetime.from_string(last_execution)
            time_diff = (fields.Datetime.now() - last_date).days
            self.can_execute = time_diff >= 90  # 90 days = quarter
        else:
            self.can_execute = True