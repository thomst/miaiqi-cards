(function() {
    "use strict";

    const showError = (error) => {
        console.error('Error reloading the shop:', error);
        alert('Error reloading the shop.');
    };

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


    // Replaces the shop html and loads the next step of the shop by its buttons.
    // After a step has been loaded by a button it is announced by a shop:#
    // event carrying the step's name (the data-step of the new shop div).
    class Shop {
        constructor () {
            document.addEventListener('click', (event) => {
                const button = event.target.closest('div.shop div.button input[data-url]');
                if (button) this.#load(button);
            });
        }

        // The button's data-url is requested by post if its data-method is "post" and
        // otherwise by get of the surrounding form.
        #load (button) {
            const url = button.dataset.url;
            const request = button.dataset.method === 'post'
                ? Ajax.post(url, button.closest('form'))
                : Ajax.get(url);
            return request
                .then((html) => this.#updateHtml(html))
                .then((shop) => this.#resetWidgets(shop))
                .catch(showError);
        }

        // Returns the new shop div.
        #updateHtml (html) {
            // Replace the whole shop div.
            const shop = document.querySelector('div.shop');
            const wrapper = document.createElement('div');
            wrapper.innerHTML = html.trim();
            const newShop = wrapper.firstChild;
            shop.replaceWith(newShop);
            return newShop;
        }

        // Update widget data to the current cart items.
        #syncWidgets (data) {
            document.querySelectorAll('.product-widget').forEach((widget) => {
                const item = data[widget.dataset.product] || {quantity: 0};
                widget.querySelector('.product-quantity').value = item.quantity;
                widget.querySelector('.product-price').value = item.quantity ? `${item.total_price} €` : '';
            });
        }

        // Resets widgets if the shop is in the confirmation step. The cart was
        // closed so we'll restart with an empty one. The widgets must be reset
        // accordingly.
        #resetWidgets (shop) {
            if (shop.dataset.step === 'confirmation') this.#syncWidgets({});
        }

        // Update widget data and update the shop html.
        update (text) {
            const json = JSON.parse(text);
            this.#syncWidgets(json.data);
            this.#updateHtml(json.html);
        }
    }


    // The widget changes the quantity of a product in the cart and updates the shop.
    class ProductWidget {
        constructor (shop) {
            this.shop = shop;
            document.addEventListener('click', (event) => {
                const button = event.target.closest('.product-widget button');
                if (button) this.#updateProduct(button);
            });
        }

        // The data-delta of the button changes the quantity of the product. The new
        // quantity is passed as get parameter to the update_product view given by
        // the data-url of the widget. It answers with the new order html and the
        // cart items.
        #updateProduct (button) {
            const widget = button.closest('.product-widget');
            const input = widget.querySelector('.product-quantity');
            const quantity = Math.max((parseInt(input.value) || 0) + parseInt(button.dataset.delta), 0);
            Ajax.get(`${widget.dataset.url}?quantity=${quantity}`)
                .then((text) => this.shop.update(text))
                .catch(showError);
        }
    }


    // Cart representation for the shop.
    class Cart {
        static CART = 'div.shop[data-step="order"]';

        constructor (shop, widgets) {
            this.shop = shop;
            this.widgets = widgets;
            document.addEventListener('click', (event) => {
                const button = event.target.closest(`${Cart.CART} input.remove-item`);
                if (button) this.#removeProduct(button);
            });
        }

        // Remove the item corresponding to the clicked button from the cart by
        // sending an Ajax request to set its quantity to 0. The server responds
        // with the updated order HTML and cart data.
        #removeProduct (button) {
            Ajax.get(`${button.dataset.url}?quantity=0`)
                .then((text) => this.shop.update(text))
                .catch(showError);
        }
    }


    const shop = new Shop();
    new ProductWidget(shop);
    new Cart(shop);
})();
