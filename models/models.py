from odoo import models, fields, api

#view created sequence 20
class StudentClassNo(models.Model):
    _name = 'student.class.no'
    _description = 'Student Class'

    name = fields.Char(string='Course', required=True)

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



class StudentClassName(models.Model):
    _name = 'student.class.name'
    _description = 'Student Class'

    name = fields.Char(string='Class Name', required=True)
    admission_fee = fields.Float('Admission Fee')
    quarter_fee = fields.Float(string='Quarter Fee', )
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

    #VIEW CREATED IN SETTINGS 10 SEQUENCE
class StudentDivision(models.Model):
    _name = 'student.division'
    _description = 'Student Division'

    name = fields.Char(string='Batch Name', required=True)
    is_locked = fields.Boolean(string='Locked', default=False)

    active = fields.Boolean(string='Active', default=True)


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


class TeacherDesignation(models.Model):
    _name = 'teacher.designation'
    _description = 'Teachers Designation'

    name = fields.Char(string='Teachers Designations')
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

class ExamName(models.Model):
    _name = 'exam.name'
    _description = 'Exam Subject Name'

    name = fields.Char(string='Exam Name')
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

class ExamSubject(models.Model):
    _name = 'exam.subject'
    _description = 'Exam Subject'

    name = fields.Char(string='Subject Name')
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



#
# class TeacherClass(models.Model):
#     _name = 'teacher.class'
#     _description = 'Teachers Class Room'
#
#     name = fields.Char(string='Teachers Class Room')