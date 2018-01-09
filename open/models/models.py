# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time

class Padre(models.Model):
    _name = 'open.padre'

    name = fields.Char(string="Nombre")
    edad = fields.Integer(string="Edad")
    fecha = fields.Date(string="Fecha de Nacimiento")
    altura = fields.Float(digits=(4, 2), help="Altura en metros")


def get_uid(self, *a):
    #import pdb; pdb.set_trace()
    return self.env.uid

class Course(models.Model):
    _name = 'open.course'

    name = fields.Char(string="Title", required=True)
    description = fields.Text()

    responsible_id = fields.Many2one(
        'res.users',
        ondelete='set null',  #cascade, restrict, set null
        string="Responsible",
        index=True,
        #default=lambda self, *a: self.env.uid #devuelve el user actual utilizando lamba
        default=get_uid #devuelve el user actual utilizando la funcion def 
    )

    session_ids = fields.One2many(
        'open.session',
        'course_id',
        string="Sessions"
    )
    



class Session(models.Model):
    _name = 'open.session'

    name = fields.Char(required=True)
    start_date = fields.Date(default=fields.Date.today)
    #datetime_test = fields.Datetime(default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')) #requiere import time
    datetime_test = fields.Datetime(default=fields.Datetime.now)
    duration = fields.Float(digits=(6, 2), help="Duración en días")
    seats = fields.Integer(string="Número de asientos")

    instructor_id = fields.Many2one(
        'res.partner',
        string="Instructor",
        domain=['|', ('instructor','=',True), ('category_id.name','ilike','Teacher')]
    )

    course_id = fields.Many2one(
        'open.course',
        ondelete='cascade',
        string="Course",
        required=True
    )

    attendee_ids = fields.Many2many(
        'res.partner',
        string="Attendees"
    )

    taken_seats = fields.Float(compute='_taken_seats')

    active = fields.Boolean(default=True) #campo reservado igual que name

    @api.depends('seats', 'attendee_ids')
    def _taken_seats(self):
        # import pdb; pdb.set_trace()
        for record in self.filtered(lambda r: r.seats):
            record.taken_seats = 100.0 * len(record.attendee_ids) / record.seats
            
        # for record in self:
        #     if not record.seats:
        #         record.taken_seats = 0
        #     else:
        #         record.taken_seats = 100.0 * len(record.attendee_ids) / record.seats
