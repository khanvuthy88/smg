# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SMGUserInfo(models.Model):
    _name = "smg.user.info"
    _inherit = ['mail.thread', 'mail.activity.mixin','portal.mixin']

    @api.multi
    def drive_selection_permission(self):
        permission = [
            ('read', 'Read'),
            ('write', 'Write'),
            ('read_and_write', 'Read & Write'),
        ]
        return permission

    @api.multi
    def department_drive_selectin_permission(self):
        permission_list=[
            ('read', 'Read'),
            ('write', 'Write'),
            ('read_and_write', 'Read & Write'),
            ('na','N/A'),
        ]
        return permission_list

    @api.multi
    def odoo_progress_state_list(self):
        odoo_progress_state_list = [
            ('draft', 'Draft'),
            ('fwd_by_it', 'FWD by IT'),
            ('requested_by_head_department', 'Requested by HR'),
            ('process_by_odoo_team', 'Processed by Odoo'),
            ('completed_by_hr', 'Complete')
        ]
        return odoo_progress_state_list

    @api.multi
    def odoo_grand_state_list(self):
        progress_state_list = [
            ('draft', 'Draft'),
            ('requested_by_head_department', 'Requested by Head'),
            ('process_by_odoo_team', 'Processed by Odoo')
        ]
        return progress_state_list

    name = fields.Char(track_visibility='always')
    state = fields.Selection([('new_user', 'New User'), ('user_movement', 'User Movement'), ('user_termination', 'User Termination')], 'State', default='new_user', track_visibility='always')
    employee_id = fields.Many2one('hr.employee', string="Employee", )
    first_name = fields.Char(string="First name")
    last_name = fields.Char(string='Last name')
    employee_id_number = fields.Char(string="Employee ID")
    telegram_id = fields.Char(string="Telegram ID")
    start_date = fields.Date(string="Start Date")
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
        ('process_by_it', 'Processed by IT'),
        ('done', 'Completed by HR'),
    ], 'Status', default='draft', track_visibility='always')

    # Noted by HR
    description = fields.Text()
    attendance_card_create = fields.Boolean(string="Access Card Created")

    # Drive access
    drive_progress_state = fields.Selection([
        ('draft', 'Draft'),
        ('requested_by_hr', 'Requested by HR'),
        ('process_by_it', 'Processed by IT'),
        ('done', 'Completed by HR'),
    ], 'Status', default='draft')

    drive_p_permission_access = fields.Selection(selection= drive_selection_permission, string='Drive P', default='read_and_write', track_visibility='always')
    drive_z_permission_access = fields.Selection(selection= drive_selection_permission, string='Drive Z', default='read_and_write', track_visibility='always')
    drive_note = fields.Text(string="Remark")

    # Odoo team

    odoo_standard_progress_state = fields.Selection(selection=odoo_progress_state_list, string='Status', default='draft')
    odoo_grant_progress_state = fields.Selection(selection=odoo_grand_state_list, string='Status', default='draft')
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

    # Access card field
    card_aceess_floor_door = fields.Many2many('smg.access_floor')
    card_access_door = fields.Selection([
        ('ground_floor','Ground Floor'),
        ('1st_floor','1st Floor'),
        ('2nd_floor','2nd Floor'),
        ('3rd_floor','3rd Floor'),
        ('4th_floor', '4th Floor'),
        ('5th_floor', '5th Floor'),
        ('6th_floor', '6th Floor'),
        ('7th_floor', '6th Floor')
    ],"Floor")

    # Add field many2many to table res.group
    # This field using in odoo tab for allow permission access to app
    user_odoo_standard_access = fields.Many2many('res.groups', domain=[('user_standard_acess', '=', True)])
    user_id = fields.Many2one('res.users')
    activity_date_deadline = fields.Date(string='Next Activity Deadline', related='activity_ids.date_deadline',
                                         groups='base.group_portal,base.group_user')

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            full_name = self.employee_id.display_name.split(" ", 1)
            self.last_name = full_name[0]
            self.first_name = full_name[1]
            self.employee_id_number = self.employee_id.smg_empid
            self.department = self.employee_id.department_id.id
            self.manager = self.employee_id.parent_id.id
            self.position = self.employee_id.job_id.id
            self.company_name = self.employee_id.company_id.id


    @api.multi
    def odoo_state_complete_by_hr(self):
        employee = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
        # Update record in res.partner by Related Partner (partner_id)
        related_partner = self.env['res.partner'].search([('id', 'in', [self.user_id.partner_id.id])])
        for record in related_partner:
            record.sudo().write({
                'parent_id': self.employee_id.address_id.id,
                'mobile': self.employee_id.mobile_phone,
                'email': self.employee_id.work_email
            })

        # Update record user_id (Related user) and address_home_id (Private Address) field in employee form to created user
        for record in employee:
            record.sudo().write({
                'address_home_id': related_partner.id,
                'user_id': self.user_id.id,
            })

        return self.sudo().write({'odoo_standard_progress_state': 'completed_by_hr'})

    @api.multi
    def odoo_grant_access_by_head(self):
        return self.sudo().write({
            'odoo_grant_progress_state': 'requested_by_head_department',
        })

    @api.multi
    def odoo_grant_access_complete_by_odoo_team(self):
        return self.sudo().write({
            'odoo_grant_progress_state': 'process_by_odoo_team',
        })

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
                partner_id = manager.address_home_id.id
                partner_ids.append(partner_id)
            else:
                partner_id = manager.user_id.partner_id.id
                partner_ids.append(partner_id)
                manager.write({
                    'address_home_id': partner_id
                })
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
        # return self.sudo().write({'it_progress_state': 'requested_by_hr'})
        self.sudo().write({'it_progress_state': 'requested_by_hr'})

        help_desk_team = self.env['helpdesk.team'].search([('id', '=', 2)])
        ticket_type = self.env['helpdesk.ticket.type'].search([('id', '=', 15)])
        ticket_tag = self.env['helpdesk.tag'].search([('id', '=', 39)])

        description = "Request create user for {}".format(self.name)
        ticket_obj = self.env['helpdesk.ticket'].sudo().create({
            'name': self.name,
            'partner_id': self.env.user.partner_id.id,
            'partner_name': self.env.user.partner_id.display_name,
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
        self.sudo().write({
            'it_progress_state': 'process_by_it',
            'odoo_user_for': self.employee_id.id,
            'odoo_requested_by': 'IT',
            'odoo_standard_progress_state': 'fwd_by_it',
            'odoo_email_address': self.initial_email,
            'odoo_username_login': self.initial_email,
            'odoo_user_password': 'Smg$123',
            # 'odoo_user_password': self.initial_password,
        })

        # Prepare to create ticket
        help_desk_team = self.env['helpdesk.team'].search([('id', '=', 1)])
        ticket_type = self.env['helpdesk.ticket.type'].search([('id', '=', 15)])
        ticket_tag = self.env['helpdesk.tag'].search([('id', '=', 42)])

        description = "Request create user for {} in Odoo system.".format(self.name)
        ticket_obj = self.env['helpdesk.ticket'].sudo().create({
            'name': self.name,
            'partner_id': self.env.user.partner_id.id,
            'partner_name': self.env.user.partner_id.display_name,
            'team_id': help_desk_team.id,
            'ticket_type_id': ticket_type.id,
            'create_user_info': self.id,
            'tag_ids': [(4, ticket_tag.id)],
            'description': description,
        })

        return ticket_obj

    @api.multi
    def completed_by_hr(self):
        for record in self.employee_id:
            record.sudo().write({'work_email': self.initial_email})
        return self.sudo().write({'it_progress_state': 'done'})

    @api.multi
    def view_user_ticket(self):
        context = dict(self.env.context)
        form_id = self.env.ref('helpdesk.helpdesk_tickets_view_tree')
        return {
            "type": "ir.actions.act_window",
            "res_model": "helpdesk.ticket",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["create_user_info", "in", [self.id]]],
        }

    @api.multi
    def odoo_complete_state(self):

        full_name = "{} {}".format(self.first_name, self.last_name)
        # Create user in odoo system
        user_obj = self.env['res.users'].sudo().create({
            'name': full_name,
            'login': self.odoo_username_login,
        })

        self.sudo().write({
            'user_id': user_obj.id,
            'odoo_standard_progress_state': 'process_by_odoo_team'
        })

        # Update record user_id (Related user) in employee form to created user
        # for record in self.employee_id:
        #     record.write({'user_id': user_obj.id})
        return user_obj


class SMGFloor(models.Model):
    _name="smg.access_floor"

    name = fields.Char()

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
                full_name = self.display_name.split(" ", 1)
                username = '{}\{}'.format('SOMAGROUP', '.'.join(split_string))
                first_name = full_name[0]
                last_name = full_name[1]
                password = 'smg@123'
                email = '@{}'.format('somagroup.com.kh')

                context = dict(
                    # default_employee_id_number = self.smg_empid,
                    default_employee_id=self.id,
                    default_name=self.name,
                    default_first_name = first_name.isupper(),
                    default_last_name = last_name.capitalize(),
                    default_department=self.department_id.id,
                    default_manager=self.parent_id.id,
                    default_position=self.job_id.id,
                    default_company_name=self.company_id.id,
                    default_username=username,
                    # default_initial_password=password,
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

    @api.multi
    def action_open_form_view(self, context=None):
        employee = self.env['smg.drive.odoo'].search([('employee_id', 'in', [self.id])])
        if employee:
            context = dict(self.env.context)
            form_id = self.env.ref('smg_create_user.smg_drive_and_odoo_form')
            return {
                'type': 'ir.actions.act_window',
                'name': 'Edit',
                'res_id': employee.id,
                'res_model': 'smg.drive.odoo',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': form_id.id,
                'context': context,
                'target': 'current',
            }
        else:
            employee_obj = self.env['hr.employee'].search([('id', 'in', [self.id])])
            employee_info = "<h1>{}</h1><ul><li>Employee Id: {}</li><li>Position:{}</li><li>Department: {}</li>".format(
                employee_obj.display_name, employee_obj.smg_empid, employee_obj.job_id.display_name,
                employee_obj.department_id.display_name)
            ctx = {
                'default_name': employee_obj.display_name,
                'default_employee_id': employee_obj.id,
                'default_employee_information': employee_info
            }
            form_id = self.env.ref('smg_create_user.smg_drive_and_odoo_form')
            return {
                'type': 'ir.actions.act_window',
                'name': 'Edit',
                'res_model': 'smg.drive.odoo',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': form_id.id,
                'context': ctx,
                'flags': {'initial_mode': 'edit'},
                'target': 'current',
            }

class SMGResgroup(models.Model):
    _inherit = ['res.groups']

    user_standard_acess = fields.Boolean(string="User Standard Access", default=False)
    user_grant_access = fields.Boolean(string="User Grant Access", default=False)


class SMGDriveAndOdoo(models.Model):
    _name="smg.drive.odoo"
    _inherit = ['mail.thread', 'mail.activity.mixin','portal.mixin']

    @api.multi
    def department_drive_selectin_permission(self):
        permission_list = [
            ('read', 'Read'),
            ('write', 'Write'),
            ('read_and_write', 'Read & Write'),
            ('na', 'N/A'),
        ]
        return permission_list

    @api.multi
    def drive_request_list(self):
        state_list = [
            ('draft','Draft'),
            ('requested_by_head','Request by Head'),
            ('it_process_completed','Processed by IT'),
            ('head_make_done','Done')
        ]
        return state_list

    @api.multi
    def odoo_request_list(self):
        state_list = [
            ('draft','Draft'),
            ('requested_by_head','Request by Head'),
            ('it_process_completed','Processed by Odoo'),
            ('head_make_done','Done')
        ]
        return state_list

    name = fields.Char()
    employee_id = fields.Many2one('hr.employee', string="Employee")
    drive_state = fields.Selection(selection=drive_request_list, string="State", default='draft', track_visibility='always')
    employee_information = fields.Text(string='Employee Info')
    odoo_state = fields.Selection(selection=odoo_request_list, string="State", default='draft', track_visibility='always')
    drive_i_permission_access = fields.Selection(selection=department_drive_selectin_permission, string='Drive I',
                                                 default='na', track_visibility='always')
    other_drive_permission_access = fields.Selection(selection=department_drive_selectin_permission,
                                                     string="Other drive",
                                                     default='na', track_visibility='always')
    drive_note = fields.Text(string="Note")
    user_odoo_grant_access = fields.Many2many('res.groups', domain=[('user_grant_access', '=', True)])
    activity_date_deadline = fields.Date(string='Next Activity Deadline', related='activity_ids.date_deadline',
                                         groups='base.group_portal,base.group_user')

    @api.multi
    def action_head_make_request_drive(self):
        return self.sudo().write({'drive_state': 'requested_by_head'})

    @api.multi
    def action_make_it_complete_by_it(self):
        return self.sudo().write({'drive_state': 'it_process_completed'})

    @api.multi
    def action_make_it_done_by_head_drive(self):
        return self.sudo().write({'drive_state': 'head_make_done'})

    @api.multi
    def action_head_make_request_odoo(self):
        return self.sudo().write({'odoo_state': 'requested_by_head'})

    @api.multi
    def action_make_it_complete_by_odoo(self):
        return self.sudo().write({'odoo_state': 'it_process_completed'})

    @api.multi
    def action_make_it_done_by_head_odoo(self):
        return self.sudo().write({'odoo_state': 'head_make_done'})

