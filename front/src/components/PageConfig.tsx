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

export interface IPageConfig {
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
    sorts: ISort[]
    themes: ITheme[]
    view_group: IViewGroup;
}
