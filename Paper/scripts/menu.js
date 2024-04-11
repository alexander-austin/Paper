/*
    Copyright (c) 2024, Alexander Austin
    All rights reserved.

    This source code is licensed under the BSD-style license found in the
    LICENSE file in the root directory of this source tree.
*/


function navigationSet() {

    const menuHandle = document.getElementById('menu-handle');
    menuHandle.classList.toggle('active');

    const menuItems = menu.querySelectorAll('.menu-item');

    for (const menuItem of menuItems) {

        menuItem.classList.remove('active');

        if (menuItem.dataset.url == window.location.pathname) {

            menuItem.classList.add('active');

        }

    }

}
