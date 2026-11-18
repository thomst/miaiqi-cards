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
            row.querySelector("input.remove-form").addEventListener('click', (event) => this.shop.removeForm(event));

            // Set event handler on inputs and selects.
            row.querySelectorAll('input:not(.remove-form), select').forEach((el) => {
                el.addEventListener('change', (event) => this.shop.updateCart(event));
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
        static ACTIONS = ['addForm', 'checkout', 'order', 'confirmation'];

        constructor () {
            this.formset = null;
            document.addEventListener('DOMContentLoaded', () => this.init());
        }

        init () {
            // Init the formset.
            const form = document.querySelector('div.shop form:has(div.form)');
            this.formset = form ? new Formset(form, this) : null;

            // Init the buttons.
            const buttons = document.querySelectorAll('div.shop div.row input[data-action]');
            for (const button of buttons) {
                const action = button.dataset.action;
                if (!Shop.ACTIONS.includes(action)) continue;
                button.addEventListener('click', (event) => this[action](event));
            }
        }

        // Actions

        updateCart (event) {
            this.#post(event);
        }

        addForm () {
            this.formset.addForm();
        }

        removeForm (event) {
            this.formset.removeForm(event);
            this.#post(event);
        }

        checkout (event) {
            this.#post(event);
        }

        order (event) {
            this.#get(event);
        }

        confirmation (event) {
            this.#post(event);
        }

        // Internals

        #get (event) {
            this.#ajaxCall(event, {
                method: "GET",
                credentials: 'same-origin',
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            });
        }

        #post (event) {
            const form = document.querySelector('div.shop > form');
            const csrftoken = form.querySelector('[name=csrfmiddlewaretoken]').value;
            this.#ajaxCall(event, {
                method: "POST",
                credentials: 'same-origin',
                body: new FormData(form),
                headers: {'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': csrftoken}
            });
        }

        #ajaxCall (event, data) {
            event.preventDefault();

            // Either take the url dataset of the target element or use the default
            // url set on the form element.
            const formUrl = document.querySelector('div.shop form')?.dataset.url;
            const url = event.target.dataset.url || formUrl;
            fetch(url, data)
            .then(function(response) {
                if (!response.ok) throw new Error(response.text());
                return response.text();
            })
            .then((html) => this.#update(html))
            .catch(function() {
                alert('Error reloading the formset.');
            });
        }

        #update (html) {
            // If we got html we replace the whole shop div and reinitialize it.
            if (html) {
                const wrapper = document.createElement('div');
                wrapper.innerHTML = html.trim();
                document.querySelector('div.shop').replaceWith(wrapper.firstChild);
                this.init();
            }
        }
    }

    window.shop = new Shop();
})();
