# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Padre(models.Model):
    _name = 'open.padre'

    name = fields.Char(string="Nombre")
    edad = fields.Integer(string="Edad")
    fecha = fields.Date(string="Fecha de Nacimiento")
    altura = fields.Float(digits=(4, 2), help="Altura en metros")


class Course(models.Model):
    _name = 'open.course'

    name = fields.Char(string="Title", required=True)
    description = fields.Text()

    responsible_id = fields.Many2one(
        'res.users',
        ondelete='set null',  #cascade, restrict, set null
        string="Responsible",
        index=True
    )

    session_ids = fields.One2many(
        'open.session',
        'course_id',
        string="Sessions"
    )
    



class Session(models.Model):
    _name = 'open.session'

    name = fields.Char(required=True)
    start_date = fields.Date()
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