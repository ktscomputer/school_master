/** @odoo-module **/

import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class StudentMasterKanbanRenderer extends KanbanRenderer {
    static components = { ...KanbanRenderer.components };

    setup() {
        super.setup();
        this.action = useService("action");
    }

    async action_new_student() {
        await this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'New Student',
            res_model: 'student.master',
            view_mode: 'kanban',
            view_type: 'kanban',
            target: 'current',
            context: {
                default_state: 'draft',
                default_active: true,
                default_is_locked: false,
                default_company_id: this.env.company.id,
            },
        });
    }
}

registry.category("views").add("student_master_kanban", {
    ...kanbanView,
    Renderer: StudentMasterKanbanRenderer,
});