from odoo import models,fields,api
import logging
_logger = logging.getLogger(__name__)

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StudentFeeReceipt(models.Model):
    _name = 'student.fee.receipt'
    _description = 'Student Fee Receipts'
    _rec_name = 'student_id'

    name = fields.Char(
        string='Receipt Number',
        readonly=True,
        default='New'
    )
    #student_id = fields.Many2one('student.master', string='Student Name')
    student_id = fields.Many2one(
        'student.master',
        string='Student Name',
        domain="[('student_class_name','=',course_id), ('student_class','=',year_id)]",
        required=True,
    )
    academic_id = fields.Many2one('student.academic', string='Academic Record', related='student_id.academic_id',
                                  store=True)
    course_id = fields.Many2one('student.class.name', string='Select Course')
    year_id = fields.Many2one('student.class.no', string='Select Year')
    amount = fields.Float(string='Amount', required=True)
    payment_date = fields.Datetime(string='Payment Date', default=fields.Datetime.now)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('card', 'Credit/Debit Card'),
        ('online', 'Online Payment')
    ], string='Payment Method', default='cash')
    reference = fields.Char(string='Payment Reference')
    collected_by = fields.Many2one(
        'res.users', string='Collected By', default=lambda self: self.env.user
    )
    is_locked = fields.Boolean(string='Locked', default=False)

    # Locking / Unlocking
    def action_save(self):
        self.write({'is_locked': True})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_edit(self):
        self.write({'is_locked': False})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    # Restrict editing if locked
    def write(self, vals):
        if any(rec.is_locked for rec in self):
            raise UserError(_("You cannot edit a locked receipt."))
        return super().write(vals)

    # Filter students by selected course and year
    @api.onchange('course_id', 'year_id')
    def _onchange_course_year(self):
        domain = {'student_id': []}
        if self.course_id and self.year_id:
            domain['student_id'] = [
                ('student_class_name', '=', self.course_id.id),
                ('student_class', '=', self.year_id.id)
            ]
            _logger.info("Filtered students for course=%s, year=%s",
                         self.course_id.name, self.year_id.name)
        elif self.course_id:
            domain['student_id'] = [('student_class_name', '=', self.course_id.id)]
            _logger.info("Filtered students for course=%s", self.course_id.name)
        elif self.year_id:
            domain['student_id'] = [('student_class', '=', self.year_id.id)]
            _logger.info("Filtered students for year=%s", self.year_id.name)
        else:
            _logger.info("No course/year selected, student list cleared")
        return {'domain': domain}

    @api.onchange('student_id')
    def _onchange_student_id(self):
        """Update course and year based on student"""
        if self.student_id:
            self.course_id = self.student_id.student_class_name.id
            self.year_id = self.student_id.student_class.id
            if self.student_id.academic_id:
                self.amount = self.student_id.academic_id.current_balance

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('student.fee.receipt') or 'New'

        records = super().create(vals_list)

        # Update academic record with payment
        for rec in records:
            if rec.academic_id and rec.amount > 0:
                try:
                    # Call the add_fee_payment method instead of direct write
                    rec.academic_id.add_fee_payment(rec.amount)

                    # Update student master record
                    rec.student_id.write({
                        'total_fees_receipted': rec.student_id.total_fees_receipted + rec.amount
                    })

                    _logger.info(
                        f"Successfully processed payment of {rec.amount} for student {rec.student_id.student_name}")

                except UserError as e:
                    # Log the error and raise it
                    _logger.error(f"Error processing payment for student {rec.student_id.student_name}: {e}")
                    raise UserError(f"Cannot create receipt: {e}")
                except Exception as e:
                    _logger.error(f"Unexpected error processing payment: {e}")
                    raise UserError(f"Unexpected error occurred: {e}")

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
            self.can_execute = time_diff = 0  # 90 days = quarter
        else:
            self.can_execute = True