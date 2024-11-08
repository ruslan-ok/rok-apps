function delCategory() {

}

const CATEGORY_DESIGN = [
    'green',
    'blue',
    'red',
    'purple',
    'yellow',
    'orange'
];

function getCategoryDesign(categ: string): string {
    const sum = Array.from(categ).reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return CATEGORY_DESIGN[sum % 6];
}

function ItemCategories({categories}: {categories: string}) {
    const categList = categories ? categories.split(',') : [];
    const categoryList = categList.map((categ, index) => {
        const design = 'category category-design-' + getCategoryDesign(categ);
        return (
            <div key={index} className={design}>
                <div className="label">
                    <div className="value">
                        {categ}
                    </div>
                </div>
                <div className="icon" onClick={delCategory}>
                    <div className="delete">
                        <svg height="8" width="8">
                            <path d="M4.46607 4L8 7.53905L7.53905 8L4 4.46607L0.460948 8L0 7.53905L3.53393 4L0 0.460948L0.460948 0L4 3.53393L7.53905 0L8 0.460948L4.46607 4Z"></path>
                        </svg>
                    </div>
                </div>
            </div>
        );
    });
    
    return (
        <div className="col-sm">
            <label htmlFor="id_categories">Categories:</label>
            <div className="categories">
                {categoryList}
            </div>
            <input type="text" id="id_categories" placeholder="Add category" className="form-control mb-3"/>
        </div>
    );
}

export default ItemCategories;