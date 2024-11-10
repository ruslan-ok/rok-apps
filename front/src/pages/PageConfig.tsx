interface IAddItem {
    type: string;
    placeholder: string;
}

interface IRelatedRole {
    name: string;
    icon: string;
    href: string;
}

export enum EntityType {
    Group,
    Folder,
}

export interface IPathItem {
    id: number;
    name: string;
    edit_url: string;
}

interface IEntity {
    type: EntityType;
    id: number;
    name: string;
    path: string | IPathItem[];
}

interface ISort {
    id: number;
    name: string;
}

interface ITheme {
    id: number;
    img: string | null;
    style: string | null;
}

interface IViewGroup {
    id: number;
    name: string;
    app: string;
    role: string;
    theme: number;
    use_sub_groups: boolean;
    act_items_qty: number;
    sub_groups: string;
    determinator: string;
    view_id: string;
    items_sort: string;
}

export class IPageConfig {
    title: string;
    icon: string;
    event_in_name: boolean;
    use_groups: boolean;
    use_selector: boolean;
    use_star: boolean;
    add_item: IAddItem | null;
    related_roles: IRelatedRole[];
    possible_related: IRelatedRole[];
    entity: IEntity;
    sorts: ISort[];
    themes: ITheme[];
    theme_id: number;
    view_group: IViewGroup;

    constructor (data: Object | unknown) {
        this.title = data?.title;
        this.icon = data?.icon;
        this.event_in_name = data?.event_in_name;
        this.use_groups = data?.use_groups;
        this.use_selector = data?.use_selector;
        this.use_star = data?.use_star;
        this.add_item = data?.add_item;
        this.related_roles = data?.related_roles;
        this.possible_related = data?.possible_related;
        this.entity = data?.entity;
        this.sorts = data?.sorts;
        this.themes = data?.themes;
        this.theme_id = data?.theme_id || 8;
        this.view_group = data?.view_group;
    }

    get isFolder(): boolean {
        return (this.entity.type === EntityType.Folder);
    }

    get folderPath(): string {
        return (this.isFolder && this.entity.path.constructor === String) ? this.entity.path : '';
    }

    get darkClass() {
        let value = '';
        if (this.view_group.theme) {
            const curTheme = this.themes.filter(x => x.id === this.theme_id);
            if ((curTheme[0].id < 8) || (curTheme[0].id > 14))
                value = ' dark-theme';
        }
        return value;
    }

    get iconClass() {
        let value = '';
        if (this.icon) {
            value = `bi-${this.icon} m-3 fs-4${this.darkClass}`;
        }
        return value;
    }

    checkDark(value: string): string {
        return value + this.darkClass;
    }
}
