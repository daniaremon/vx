# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import timedelta
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
    
    #variable reservada, para saber mas sql constraints se debee leer la documentacion de odoo
    #si al momento de crear el constraint sql, en la base algún registro está rompiendo estos constraints, 
    # se genera un error y no se permite crear el constraint (en el log obtendremos un warning)
    _sql_constraints = [
        ('name_description_check',
         'CHECK( name != description )',
         "The title of the course should not be the description"
        ),
        ('name_unique',
         'UNIQUE(name)',
         "The course title must be unique"
        ),
    ]

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', 'ilike', u"Copy of {}%".format(self.name))])

        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)

        default['name'] = new_name
        # try:
        return super(Course, self).copy(default)
        # except IntegrityError:
        #     import pdb; pdb.set_trace()


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

    taken_seats = fields.Float(compute='_taken_seats', store=True) #agregando store=True se agrega a la base de datos y se pueden usar constraints sql
    #no en todos los casos se debe usar strore=True porque hay casos en los que solo se reuqiere ese momento, dependiendo el caso pueden entrar 2 usuario y querer grabar al mismo tiempo y pueden dar problemas, como en inventario

    active = fields.Boolean(default=True) #campo reservado igual que name
    end_date = fields.Date(store=True, compute='_get_end_date')
    attendees_count = fields.Integer(
        string="Attendees count", compute='_get_attendees_count', store=True)
    color = fields.Integer()

    hours = fields.Float(string="Duration in hours",
                         compute='_get_hours', inverse='_set_hours')


    @api.depends('duration')
    def _get_hours(self):
        for r in self:
            r.hours = r.duration * 24

    def _set_hours(self):
        for r in self:
            r.duration = r.hours / 24
            
    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = len(r.attendee_ids)

    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        #import pdb; pdb.set_trace()
        for record in self.filtered('start_date'):
            start_date = fields.Datetime.from_string(record.start_date)
            record.end_date = start_date + timedelta(days=record.duration, seconds=-1)


    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue
            # Compute the difference between dates, but: Friday - Monday = 4 days,
            # so add one day to get 5 days instead
            start_date = fields.Datetime.from_string(r.start_date)
            end_date = fields.Datetime.from_string(r.end_date)
            r.duration = (end_date - start_date).days + 1


    @api.depends('seats', 'attendee_ids')
    def _taken_seats(self):
        #import pdb; pdb.set_trace()
        for record in self.filtered(lambda r: r.seats):
            record.taken_seats = 100.0 * len(record.attendee_ids) / record.seats
            
        # for record in self:
        #     if not record.seats:
        #         record.taken_seats = 0
        #     else:
        #         record.taken_seats = 100.0 * len(record.attendee_ids) / record.seats

    @api.onchange('seats','attendee_ids') #solo se dispara en la vista de captura, y self solo tiene 1 record
    def _verify_valid_seats(self):
        if self.filtered(lambda r: r.seats < 0):  #if self.seats<0:
            self.active = False
            return{
                'warning':{
                    'tittle': "Incorrect 'seats' value",
                    'message': "The number of available seats may not be negative",
                }
             }
        if self.seats<len(self.attendee_ids):
            self.active=False
            return{
                'warning':{
                    'tittle': "Too many attendees",
                    'message': "Invrease seats or remove attendees excess",
                }
            }
        self.active = True

    #constrins se dispara cuando le doy en Save, y se ejecutan por la ORM si se hace un insert directo a la base no se ejecuta esta regla
    @api.constrains('instructor_id','attendee_ids') #ojooooooo  ya existía una vieja forma de hacer constrints por eso el nombre ahora es constrins sin la t
    def _check_instructor_not_in_attendees(self):
        for record in self.filtered('instructor_id'): #filtered permite predicate function, un campo bool escrito entre "" , y un campo '' cualquiera para qeu verifique si existe 
            if record.instructor_id in record.attendee_ids:
                raise exceptions.ValidationError(
                        "A sessio's instructor can't be an attendee") #necesita import exceptions .. esto se encuentra en exceptions.py

    