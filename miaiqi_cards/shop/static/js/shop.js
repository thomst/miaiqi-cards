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

        constructor () {
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

        // The cart is saved on the server without reloading the shop.
        save (form) {
            Ajax.post(form.dataset.url, form).catch(showError);
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
            return request.then((html) => this.update(html)).catch(showError);
        }

        update (html) {
            // Replace the whole shop div.
            const shop = document.querySelector('div.shop');
            if (html && shop) {
                const wrapper = document.createElement('div');
                wrapper.innerHTML = html.trim();
                shop.replaceWith(wrapper.firstChild);
            }
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
    new Formset();
    new ProductWidget(shop);
})();
