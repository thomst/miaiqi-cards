(function() {
    "use strict";

    class Formset {
        constructor (form, shop) {
            this.form = form;
            this.shop = shop;
            this.totalInput = form.querySelector('input[id$="-TOTAL_FORMS"]');
            this.total = parseInt(this.totalInput.value);
            this.form.querySelectorAll('div.form').forEach((el => {
                this.initEventHandlers(el);
            }))
        }
        initEventHandlers(row) {
            // Set event handler on remove button.
            row.querySelector("input.remove-form").addEventListener(
                'click', (event) => this.shop.removeForm(event)
            );

            // Set event handler on inputs and selects.
            row.querySelectorAll('input:not(.remove-form), select').forEach((el) => {
                el.addEventListener('change', (event) => this.shop.post(event));
            });
        }

        updateFormCount () {
            this.form.querySelectorAll('div.form').forEach((div, index) => {
                div.querySelectorAll('[name^="form-"]').forEach(element => {
                    element.name = element.name.replace(/form-\d/, `form-${index}`);
                    element.id = element.id.replace(/form-\d/, `form-${index}`);
                });
            });
        }
        addForm () {
            this.total++;
            this.totalInput.value = this.total;
            const firstForm = this.form.querySelector('div:nth-child(1 of .form)');
            const lastForm = this.form.querySelector('div:nth-last-child(1 of .form)');
            const newForm = firstForm.cloneNode(true);
            newForm.querySelectorAll('[name^="form-"]').forEach(element => { element.value = ''; });
            this.initEventHandlers(newForm);
            lastForm.after(newForm);
            this.updateFormCount();
        }
        removeForm (event) {
            if (this.total == 1) {
                const form = event.target.parentNode.parentNode;
                form.querySelectorAll('[name^="form-"]').forEach(element => { element.value = ''; });
                form.querySelector('input[name^="form-"]').value = '';
            } else {
                this.total--;
                this.totalInput.value = this.total;
                event.target.parentNode.parentNode.remove();
                this.updateFormCount();
            }
        }
    }


    class Shop {
        // Actions available for the buttons via their data-action attribute.
        static ACTIONS = ['addForm', 'get', 'post'];

        constructor () {
            this.formset = null;
            document.addEventListener('DOMContentLoaded', () => {
                this.init();
                this.initProductWidgets();
            });
        }

        init () {
            // Init the formset.
            const form = document.querySelector('div.shop form:has(div.form)');
            this.formset = form ? new Formset(form, this) : null;

            // Init the buttons.
            const buttons = document.querySelectorAll('div.shop div.row input[data-action]');
            for (const button of buttons) {
                const action = button.dataset.action || 'post';
                if (!Shop.ACTIONS.includes(action)) continue;
                button.addEventListener('click', (event) => this[action](event));
            }
        }

        // The product widgets live outside of the shop div, so they are not replaced
        // by #update and must be initialized only once.
        initProductWidgets () {
            const buttons = document.querySelectorAll('.product-widget button');
            for (const button of buttons) {
                button.addEventListener('click', (event) => this.updateProduct(event));
            }
        }

        // Actions

        addForm () {
            this.formset.addForm();
        }

        removeForm (event) {
            const url = this.#getUrl(event);
            this.formset.removeForm(event);
            this.post(event, url);
        }

        updateProduct (event) {
            // The data-delta of the button changes the quantity of the product. The
            // new quantity is passed as get parameter to the update_product view
            // given by the data-url of the widget.
            const button = event.currentTarget;
            const input = button.closest('.product-widget').querySelector('input');
            const quantity = Math.max((parseInt(input.value) || 0) + parseInt(button.dataset.delta), 0);
            const url = this.#getUrl(event) + '?quantity=' + quantity;
            this.get(event, url).then((success) => {
                if (success) input.value = quantity;
            });
        }

        get (event, url = null) {
            return this.#ajaxCall(event, {
                method: "GET",
                credentials: 'same-origin',
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            }, url);
        }

        post (event, url = null) {
            const form = document.querySelector('div.shop > form');
            const csrftoken = form.querySelector('[name=csrfmiddlewaretoken]').value;
            return this.#ajaxCall(event, {
                method: "POST",
                credentials: 'same-origin',
                body: new FormData(form),
                headers: {'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': csrftoken}
            }, url);
        }

        // Internals

        #getUrl (event) {
            // Take the url from the closest parent element with a data-url
            // attribute.
            return event.target.closest('[data-url]')?.dataset.url;
        }

        // Returns a promise resolving to true on success and to false on failure.
        #ajaxCall (event, data, url = null) {
            event.preventDefault();

            url = url || this.#getUrl(event);
            return fetch(url, data)
            .then((response) => {
                if (!response.ok) throw new Error(response.text());
                return response.text();
            })
            .then((html) => {
                this.#update(html);
                return true;
            })
            .catch(() => {
                alert('Error reloading the formset.');
                return false;
            });
        }

        #update (html) {
            // If we got html we replace the whole shop div and reinitialize it.
            const shop = document.querySelector('div.shop');
            if (html && shop) {
                const wrapper = document.createElement('div');
                wrapper.innerHTML = html.trim();
                shop.replaceWith(wrapper.firstChild);
                this.init();
            }
        }
    }

    window.shop = new Shop();
})();
