(function() {
    "use strict";

    const showError = () => alert('Error reloading the shop.');


    // Requests to the shop views. They return a promise resolving to the response text.
    class Ajax {
        static get (url) {
            return Ajax.#request(url, {method: "GET"});
        }

        static post (url, form) {
            const csrftoken = form.querySelector('[name=csrfmiddlewaretoken]').value;
            return Ajax.#request(url, {
                method: "POST",
                body: new FormData(form),
                headers: {'X-CSRFToken': csrftoken}
            });
        }

        static #request (url, options) {
            options.credentials = 'same-origin';
            options.headers = {'X-Requested-With': 'XMLHttpRequest', ...options.headers};
            return fetch(url, options).then((response) => {
                if (!response.ok) throw new Error(response.statusText);
                return response.text();
            });
        }
    }


    // Everything that belongs to the order form. The handlers are delegated to the
    // document, so they survive the replacement of the shop html.
    class Formset {
        static FORM = 'div.shop form:has(div.form)';

        constructor (widgets) {
            this.widgets = widgets;
            document.addEventListener('click', (event) => this.#onClick(event));
            document.addEventListener('change', (event) => this.#onChange(event));
        }

        addForm (form) {
            const rows = form.querySelectorAll('div.form');
            const newRow = rows[0].cloneNode(true);
            newRow.querySelectorAll('[name^="form-"]').forEach(element => { element.value = ''; });
            rows[rows.length - 1].after(newRow);
            this.#updateFormCount(form);
        }

        removeForm (form, row) {
            if (form.querySelectorAll('div.form').length == 1) {
                row.querySelectorAll('[name^="form-"]').forEach(element => { element.value = ''; });
            } else {
                row.remove();
                this.#updateFormCount(form);
            }
            this.save(form);
        }

        // The cart is saved on the server without reloading the shop. The server
        // answers with the quantities of the cart to keep the widgets in sync.
        save (form) {
            return Ajax.post(form.dataset.url, form)
                .then((text) => this.widgets.sync(JSON.parse(text)))
                .catch(showError);
        }

        #updateFormCount (form) {
            const rows = form.querySelectorAll('div.form');
            form.querySelector('input[id$="-TOTAL_FORMS"]').value = rows.length;
            rows.forEach((row, index) => {
                row.querySelectorAll('[name^="form-"]').forEach(element => {
                    element.name = element.name.replace(/form-\d+/, `form-${index}`);
                    element.id = element.id.replace(/form-\d+/, `form-${index}`);
                });
            });
        }

        #onClick (event) {
            const button = event.target.closest(`${Formset.FORM} input[type="button"]`);
            if (!button) return;
            const form = button.closest('form');
            if (button.classList.contains('add-form')) {
                this.addForm(form);
            } else if (button.classList.contains('remove-form')) {
                this.removeForm(form, button.closest('div.form'));
            }
        }

        #onChange (event) {
            const row = event.target.closest(`${Formset.FORM} div.form`);
            if (row) this.save(row.closest('form'));
        }
    }


    // Replaces the shop html and loads the next step of the shop by its buttons.
    // After a step has been loaded by a button it is announced by a shop:load
    // event carrying the step's name (the data-step of the new shop div).
    class Shop {
        constructor () {
            document.addEventListener('click', (event) => {
                const button = event.target.closest('div.shop input[data-url]');
                if (button) this.load(button);
            });
        }

        // The button's data-url is requested by get if its data-method is "get" and
        // otherwise by post of the surrounding form.
        load (button) {
            const url = button.dataset.url;
            const request = button.dataset.method === 'get'
                ? Ajax.get(url)
                : Ajax.post(url, button.closest('form'));
            return request
                .then((html) => this.update(html))
                .then((shop) => this.dispatchLoad(shop))
                .catch(showError);
        }

        // Returns the new shop div or null if nothing was replaced.
        update (html) {
            // Replace the whole shop div.
            const shop = document.querySelector('div.shop');
            if (html && shop) {
                const wrapper = document.createElement('div');
                wrapper.innerHTML = html.trim();
                const newShop = wrapper.firstChild;
                shop.replaceWith(newShop);
                return newShop;
            }
            return null;
        }

        // Dispatches a shop:load event with the new shop div as detail.
        dispatchLoad (shop) {
            if (shop) document.dispatchEvent(new CustomEvent('shop:load', {detail: shop}));
        }
    }


    // The widget changes the quantity of a product in the cart and updates the shop.
    class ProductWidget {
        constructor (shop) {
            this.shop = shop;
            document.addEventListener('click', (event) => {
                const button = event.target.closest('.product-widget button');
                if (button) this.changeQuantity(button);
            });

            // The purchase closes the cart, so the next one starts empty.
            document.addEventListener('shop:load', (event) => {
                if (event.detail.dataset.step === 'confirmation') this.sync({});
            });
        }

        // Set the quantity of every widget to the one of its product in the given
        // quantities, which are keyed by product id. Missing products count as 0.
        sync (quantities) {
            document.querySelectorAll('.product-widget').forEach((widget) => {
                widget.querySelector('input').value = quantities[widget.dataset.product] || 0;
            });
        }

        // The data-delta of the button changes the quantity of the product. The new
        // quantity is passed as get parameter to the update_product view given by
        // the data-url of the widget.
        changeQuantity (button) {
            const widget = button.closest('.product-widget');
            const input = widget.querySelector('input');
            const quantity = Math.max((parseInt(input.value) || 0) + parseInt(button.dataset.delta), 0);
            return Ajax.get(`${widget.dataset.url}?quantity=${quantity}`)
                .then((html) => {
                    this.shop.update(html);
                    input.value = quantity;
                })
                .catch(showError);
        }
    }

    const shop = new Shop();
    const widgets = new ProductWidget(shop);
    new Formset(widgets);
})();
