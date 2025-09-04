/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { registry } from "@web/core/registry";
import { formView } from "@web/views/form/form_view";

export class StudentMasterFormController extends FormController {
    setup() {
        super.setup();
    }

    async _onButtonClicked(event) {
        if (event.data.attrs.name === "action_cancel") {
            await this.model.discardChanges(this.handle);
            await this.actionService.doAction({
                type: 'ir.actions.act_window',
                name: 'Student Master',
                res_model: 'student.master',
                view_mode: 'list',
                view_type: 'list',
                target: 'main',
            });
        } else {
            await this._super(...arguments);
        }
    }
}

registry.category("views").add("student_master_form", {
    ...formView,
    Controller: StudentMasterFormController,
});