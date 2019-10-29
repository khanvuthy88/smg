# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SMGUserInfo(models.Model):
    _name = "smg.user.info"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.multi
    def drive_selection_permission(self):
        permission = [
            ('read', 'Read'),
            ('write', 'Write'),
            ('read_and_write', 'Read & Write'),
        ]
        return permission

    name = fields.Char()
    employee_id = fields.Many2one('hr.employee', string="Employee")
    first_name = fields.Char(string="First name")
    last_name = fields.Char(string='Last name')
    employee_id_number = fields.Char(string="Employee Number")
    telegram_id = fields.Char(string="Telegram ID")
    start_date = fields.Date(string="Start Date", default=fields.Date.today)
    company_name = fields.Many2one('res.partner', string="Company name")
    department = fields.Many2one('hr.department', string="Department")
    position = fields.Many2one('hr.job', string="Position")
    manager = fields.Many2one('hr.employee', string="Manager")

    # Create user notepad
    username = fields.Char(string="User name")
    initial_password = fields.Char(string="Initial Password")
    initial_email = fields.Char(string="Initial Email")
    it_progress_state = fields.Selection([
        ('draft', 'Draft'),
        ('requested_by_hr', 'Requested by HR'),
        ('process_by_it', 'Process by IT'),
        ('done', 'Completed by HR'),
    ], 'Status', default='draft')

    # Noted by HR
    description = fields.Text()
    attendance_card_create = fields.Boolean(string="Attendance Card Created")

    # Drive access
    drive_progress_state = fields.Selection([
        ('draft', 'Draft'),
        ('requested_by_hr', 'Requested by HR'),
        ('process_by_it', 'Process by IT'),
        ('done', 'Completed by HR'),
    ], 'Status', default='draft')

    drive_i_permission_access = fields.Selection(selection= drive_selection_permission, string='Drive I', default='read')
    drive_p_permission_access = fields.Selection(selection= drive_selection_permission, string='Drive P', default='read_and_write')
    drive_z_permission_access = fields.Selection(selection= drive_selection_permission, string='Drive Z', default='read_and_write')
    other_drive_permission_access = fields.Selection(selection=drive_selection_permission, string="Other drive", default='read')

    drive_note = fields.Text(string="Remark")

    # Odoo team

    odoo_progress_state = fields.Selection([
        ('draft', 'Draft'),
        ('requested_by_hr', 'Requested by HR'),
        ('fwd_by_it', 'FWD by IT'),
        ('process_by_odoo_team', 'Processed by Odoo'),
    ], 'Status', default='draft')
    odoo_user_for = fields.Many2one('hr.employee', string="Employee Name")
    odoo_requested_by = fields.Char(string="Req By")
    odoo_email_address = fields.Char(string="Email Address")
    odoo_username_login = fields.Char(string="User login")
    odoo_user_password = fields.Char(string="Password")

    # Account user notebook
    account_progress_state = fields.Selection([
        ('draft', 'Draft'),
        ('requested_by_hr', 'Requested by HR'),
        ('process_by_it', 'Process by IT'),
        ('done', 'Completed by HR'),
    ], 'Status', default='draft')
    sage_access = fields.Boolean(string="Sage System")
    quickbook = fields.Boolean(string='Quickbook')
    peachtree = fields.Boolean(string='Peachtree')
    account_remark = fields.Text(string="Remark")
    ticket_ids = fields.One2many('helpdesk.ticket', 'create_user_info', 'Tickets')
    has_ticket = fields.Boolean(string="Has ticket", compute="_get_ticket_by_self")

    @api.model
    def create(self, vals):
        # Add employee and his manager to follower but to add follower is possible only partner (res.partner) and user(
        # res.user) and hr.employee relation with res.partner with field : Private Address (address_home_id)

        partner_ids = []
        employee = self.env['hr.employee'].search([('id', '=', vals['employee_id'])])
        if employee.address_home_id:
            partner_ids.append(employee.address_home_id.id)
        if 'manager' in vals:
            manager = self.env['hr.employee'].search([('id', '=', vals['manager'])])
            if manager.address_home_id:
                partner_ids.append(manager.address_home_id.id)
        user = super(SMGUserInfo, self).create(vals)
        if partner_ids:
            user.message_subscribe(partner_ids=partner_ids)
        return user

    @api.depends('ticket_ids')
    def _get_ticket_by_self(self):
        for record in self:
            if not record.ticket_ids:
                record.has_ticket = False
            else:
                record.has_ticket = True

    @api.multi
    def create_ticket_tags(self, vals):
        ticket_obj = self.env['helpdesk.ticket'].create({
            'name': vals['name'],
            'team_id': vals['help_desk_team'],
            'ticket_type_id': vals['ticket_type'],
            'description': ['description'],
        })

    @api.multi
    def requested_by_hr(self):
        # return self.write({'it_progress_state': 'requested_by_hr'})
        self.write({'it_progress_state': 'requested_by_hr'})

        help_desk_team = self.env['helpdesk.team'].search([('id', '=', 2)])
        ticket_type = self.env['helpdesk.ticket.type'].search([('id', '=', 15)])
        ticket_tag = self.env['helpdesk.tag'].search([('id', '=', 39)])

        description = "Request create user for {}".format(self.name)
        ticket_obj = self.env['helpdesk.ticket'].create({
            'name': self.name,
            'team_id': help_desk_team.id,
            'ticket_type_id': ticket_type.id,
            'create_user_info': self.id,
            'tag_ids': [(4, ticket_tag.id)],
            'description': description,
        })

        return ticket_obj

    @api.multi
    def precessed_by_it(self):
        # Update IT state and update Odoo tab Field
        self.write({
            'it_progress_state': 'process_by_it',
            'odoo_user_for': self.employee_id.id,
            'odoo_requested_by': 'IT',
            'odoo_progress_state': 'fwd_by_it',
            'odoo_email_address': self.initial_email,
            'odoo_username_login': self.initial_email,
            'odoo_user_password': self.initial_password,
        })

        # Prepare to create ticket
        help_desk_team = self.env['helpdesk.team'].search([('id', '=', 1)])
        ticket_type = self.env['helpdesk.ticket.type'].search([('id', '=', 15)])
        ticket_tag = self.env['helpdesk.tag'].search([('id', '=', 42)])

        description = "Request create user for {} in Odoo system.".format(self.name)
        ticket_obj = self.env['helpdesk.ticket'].create({
            'name': self.name,
            'team_id': help_desk_team.id,
            'ticket_type_id': ticket_type.id,
            'create_user_info': self.id,
            'tag_ids': [(4, ticket_tag.id)],
            'description': description,
        })

        for record in self.employee_id:
            record.write({'work_email': self.initial_email})

        return ticket_obj

    @api.multi
    def completed_by_hr(self):
        return self.write({'it_progress_state': 'done'})

    @api.multi
    def view_user_ticket(self):
        context = dict(self.env.context)
        form_id = self.env.ref('helpdesk.helpdesk_tickets_view_tree')
        # employee_ticket = self.env['helpdesk.ticket'].search([('create_user_info','=', [self.id])])
        print("This is domain id {}".format(self.ticket_ids))
        return {
            "type": "ir.actions.act_window",
            "res_model": "helpdesk.ticket",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["create_user_info", "in", [self.id]]],
        }

    @api.multi
    def odoo_complete_state(self):
        # Update odoo state
        self.write({'odoo_progress_state': 'process_by_odoo_team'})

        # Create user in odoo system
        user_obj = self.env['res.users'].create({
            'name': self.odoo_user_for.display_name,
            'login': self.odoo_username_login,
        })

        # Update record user_id (Related user) in employee form to created user
        for record in self.employee_id:
            record.write({'user_id': user_obj.id})
        return user_obj


class SMGTicket(models.Model):
    _inherit = ['helpdesk.ticket']

    create_user_info = fields.Many2one('smg.user.info', 'Create User flow')

    @api.multi
    def view_create_user_info(self):
        self.ensure_one()
        user = self.env['smg.user.info'].search([('id', '=', self.create_user_info.id)])
        context = dict(self.env.context)
        # context['form_view_initial_mode'] = 'edit'
        form_id = self.env.ref('smg_create_user.smg_create_user_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Edit',
            'res_model': 'smg.user.info',
            'res_id': user.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': form_id.id,
            'context': context,
            # 'flags': {'initial_mode': 'edit'},
            'target': 'current',
        }


class SMGEmployee(models.Model):
    _inherit = 'hr.employee'

    def lower_string(self, vals):
        return vals.lower()

    def split_string(self, vals):
        return vals.split(' ')

    @api.multi
    def return_action_to_open(self):
        # self.ensure_one()
        user = self.env['smg.user.info'].search([('employee_id', '=', self.id)])
        if user.employee_id.id == self.id:
            context = dict(self.env.context)
            # context['form_view_initial_mode'] = 'edit'
            form_id = self.env.ref('smg_create_user.smg_create_user_form')
            return {
                'type': 'ir.actions.act_window',
                'name': 'Edit',
                'res_model': 'smg.user.info',
                'res_id': user.id,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': form_id.id,
                'context': context,
                # 'flags': {'initial_mode': 'edit'},
                'target': 'current',
            }
        else:
            xml_id = self.env.context.get('xml_id')
            if xml_id:
                res = self.env['ir.actions.act_window'].for_xml_id('smg_create_user', xml_id)
                lower_string = self.lower_string(self.name)
                split_string = self.split_string(lower_string)
                username = '-'.join(split_string)
                password = 'smg@123'
                email = '{}@{}'.format(username, 'somagroup.com.kh')

                context = dict(
                    default_employee_id=self.id,
                    default_name=self.name,
                    default_department=self.department_id.id,
                    default_manager=self.parent_id.id,
                    default_position=self.job_id.id,
                    default_company_name=self.address_id.id,
                    default_username=username,
                    default_initial_password=password,
                    default_initial_email=email,
                    group_by=False
                )
                context['form_view_initial_mode'] = 'edit'
                form_id = self.env.ref('smg_create_user.smg_create_user_form')
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Edit',
                    'res_model': 'smg.user.info',
                    'res_id': user.id,
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': form_id.id,
                    'context': context,
                    'flags': {'initial_mode': 'edit'},
                    'target': 'current',
                }

        return False
