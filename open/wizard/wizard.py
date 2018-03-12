# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Wizard(models.TransientModel):
    _name = 'open.wizard'

    def _default_session(self):
        return self.env['open.session'].browse(self._context.get('active_ids'))

    session_ids = fields.Many2many(
        'open.session',
        required = True,
        default=_default_session
    )
    attendee_ids = fields.Many2many('res.partner')

    @api.multi
    def subscribe(self):
        for session in self.session_ids:
            session.attendee_ids |= self.attendee_ids
        return {}