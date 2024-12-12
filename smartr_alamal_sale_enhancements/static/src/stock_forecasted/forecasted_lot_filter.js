/** @odoo-module **/

import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

export class ForecastedLotFilter extends Component {
    static template = "smartr_alamal_sale_enhancements.ForecastedLotFilter";
    static components = { Dropdown, DropdownItem };
    static props = { action: Object, setLotInContext: Function, lots: Array };

    setup() {
        this.orm = useService("orm");
        this.context = this.props.action.context;
        this.lots = this.props.lots;
        onWillStart(this.onWillStart)
    }

    async onWillStart() {
        this.displayLotFilter = (this.lots.length > 1);
    }

    _onSelected(id){
        this.props.setLotInContext(Number(id));
    }

    get activeLot() {
        let lotIds = null;
        if (Array.isArray(this.context.lot_id)) {
            lotIds = this.context.lot_id;
        } else {
            lotIds = [this.context.lot_id];
        }
        return lotIds
            ? this.lots.find((w) => lotIds.includes(w.id))
            : this.lots[0];
    }

    get lotsItems() {
        return this.lots.map(lot => ({
            id: lot.id,
            label: lot.name,
            class: { selected: lot == this.activeLot},
            onSelected: () => this._onSelected(lot.id),
        }));
    }
}
