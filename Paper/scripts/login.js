/*
    Copyright (c) 2024, Alexander Austin
    All rights reserved.

    This source code is licensed under the BSD-style license found in the
    LICENSE file in the root directory of this source tree.
*/


window.onload = function () {

    const passwordInput = document.getElementById('login-password');

    passwordInput.addEventListener(
        'keyup',
        function (e) {

            if (e.isComposing) {
                return;
            }

            const passwordInput = document.getElementById('login-password');
            passwordInput.classList.remove('password-bad');
            passwordInput.classList.remove('password-good');

            const passwordRegexDiv = document.getElementById('password-regex');
            const passwordRegex = passwordRegexDiv.dataset.passwordRegex;

            const password = passwordInput.value;

            if (password.length > 0) {

                if (password.match(passwordRegex) == null) {

                    passwordInput.classList.add('password-bad');

                } else {

                    passwordInput.classList.add('password-good');

                }

            }

        }

    );

}
