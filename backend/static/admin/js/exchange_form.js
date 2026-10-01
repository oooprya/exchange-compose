// Парсинг кросс-курса с приоритетом usd
function parseCrossRate(code) {
    if (!code || typeof code !== "string") return null;

    const match = code.match(/^([a-z]{3})-([a-z]{3})$/i);
    if (!match) return null;

    let [_, cur1, cur2] = match;
    cur1 = cur1;
    cur2 = cur2;

    // Если есть usd — делаем его base
    if (cur1 === "usd" || cur2 === "usd") {
        return {
            baseCurrency: "usd",
            quoteCurrency: cur1 === "usd" ? cur2 : cur1
        };
    }

    // Обычный кросс без usd
    return {
        baseCurrency: cur1,
        quoteCurrency: cur2
    };
}

// Проверяет, помечена ли опция как кросс-валюта (data-is-cross="1"/"true").
function isOptionCross(option) {
    if (!option) return false;
    const ds = option.dataset || {};
    if (ds.isCross !== undefined) {
        return ds.isCross === '1' || ds.isCross === 'true';
    }
    const code = option.getAttribute && option.getAttribute('data-code');
    return !!(code && code.includes('-'));
}

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById('exchange-form');
    const button = document.getElementById('exchange-submit');
    const submitText = document.getElementById('submit-text');
    const spinner = document.getElementById('submit-spinner');
    const loading = document.getElementById('exchange-loading');

    const currencyField = document.querySelector("[name='currency']");
    const balanceEl = document.getElementById("current-balance");
    const amountInput = document.getElementById("amount");
    const rateInput = document.getElementById("rate");
    const configElement = document.getElementById("exchange-form-config");
    const balanceUrl = configElement?.dataset.balanceUrl || "/admin/wholesale/get-balance/";
    const collectionBalances = document.querySelectorAll(".collection-balance");
    document.querySelectorAll(".collection-balance-amount").forEach((amount) => {
        const numericValue = Number(
            amount.dataset.value.replace(/[\s\u00a0\u202f]/g, "")
        );
        if (Number.isFinite(numericValue)) {
            amount.textContent = numericValue.toLocaleString("ru-RU");
        }
    });

     if (!form || !button) {
        return;
    }

    let submitted = false;

    form.addEventListener('submit', function (event) {

        // Защита от двойного клика
        if (submitted) {
            event.preventDefault();
            return;
        }

        submitted = true;

        // Блокируем кнопку
        button.disabled = true;

        // Меняем текст
        submitText.classList.add('hidden');
        spinner.classList.remove('hidden');

        // Показываем overlay
        if (loading) {
            loading.classList.remove('hidden');
        }

    });

    function updateCrossRateUI(currencyId) {
        const selectedOption = currencyField.querySelector(`option[value="${currencyId}"]`);
        const code = selectedOption?.getAttribute('data-code');
        const orderType = document.querySelector('[name="order_type"]').value;

        const crossInfo = code ? parseCrossRate(code) : null;
        const uahEquiv = document.getElementById("uah-equiv");
        const crossEquiv = document.getElementById("cross-equiv");
        const balanceCurrencyLabel = document.getElementById("balance-currency-label");
        const baseCurrencySelectWrapper = document.getElementById("base-currency-select-wrapper");

        if (crossInfo) {
            // Это кроссовый курс
            if (uahEquiv) uahEquiv.style.display = "none";
            if (crossEquiv) crossEquiv.style.display = "block";

            // Обновляем rate input если он существует
            if (rateInput) {
                rateInput.required = false;
                rateInput.value = "";
            }

            // Показываем селект для выбора версии базовой валюты
            if (baseCurrencySelectWrapper) {
                baseCurrencySelectWrapper.style.display = "block";
                populateBaseCurrencySelect(crossInfo.baseCurrency);
            }

            // Обновляем label селекта в зависимости от типа операции
            const baseCurrencyLabel = document.querySelector('#base-currency-select-wrapper label');
            if (baseCurrencyLabel) {
                if (orderType === "buy") {
                    baseCurrencyLabel.innerText = "⬆ Доллар клієнту?";
                } else if (orderType === "sell") {
                    baseCurrencyLabel.innerText = "⬇ Доллар прийшов від клієнта?";
                }
            }

            // Обновляем лейблы кроса
            const baseCurrencyCodeSpan = document.getElementById("base-currency-code");
            if (baseCurrencyCodeSpan) baseCurrencyCodeSpan.innerText = crossInfo.baseCurrency;

            // Показываем правильный баланс в зависимости от типа операции
            if (balanceCurrencyLabel) {
                if (orderType === "buy") {
                    balanceCurrencyLabel.innerText = crossInfo.baseCurrency;
                } else if (orderType === "sell") {
                    balanceCurrencyLabel.innerText = crossInfo.quoteCurrency;
                }
            }
        } else {
            // Обычный курс
            if (uahEquiv) uahEquiv.style.display = "block";
            if (crossEquiv) crossEquiv.style.display = "none";

            if (rateInput) {
                rateInput.required = true;
            }

            if (baseCurrencySelectWrapper) {
                baseCurrencySelectWrapper.style.display = "none";
            }

            // Показываем баланс выбранной валюты
            if (balanceCurrencyLabel) {
                balanceCurrencyLabel.innerText = code || "";
            }
        }
    }

    function populateBaseCurrencySelect(baseCurrency) {
        const baseCurrencySelect = document.getElementById("base_currency");
        if (!baseCurrencySelect) return;

        // Получаем все доступные валюты для этой базовой валюты
        const allOptions = Array.from(currencyField.options).map(opt => ({
            id: opt.value,
            code: opt.getAttribute('data-code'),
            name: opt.textContent,
            isCross: (opt.dataset && (opt.dataset.isCross === '1' || opt.dataset.isCross === 'true')) || (opt.getAttribute && !!(opt.getAttribute('data-code') || '').includes('-'))
        }));

        // Фильтруем валюты, которые относятся к базовой валюте (USD, USDnew и т.д., но исключаем кроссовые курсы USD-EUR)
        const matchingCurrencies = allOptions.filter(curr => {
            if (!curr.code) return false;
            const code = curr.code.toLowerCase();
            const base = baseCurrency.toLowerCase();

            // Исключаем кроссовые курсы (по явному флагу или дефису в коде)
            if (curr.isCross) return false;

            // Проверяем совпадение: точное или варианты без дефиса
            return code === base || (code.startsWith(base) && code.length > base.length);
        });

        // Заполняем селект
        baseCurrencySelect.innerHTML = '';
        matchingCurrencies.forEach(curr => {
            const option = document.createElement('option');
            option.value = curr.id;
            option.textContent = curr.name;
            option.setAttribute('data-code', curr.code);
            baseCurrencySelect.appendChild(option);
        });

        // Если есть опции, устанавливаем первую как выбранную
        if (baseCurrencySelect.options.length > 0) {
            baseCurrencySelect.value = baseCurrencySelect.options[0].value;
            baseCurrencySelect.addEventListener('change', function () {
                loadBalance(currencyField.value);
            });
        }
    }

    function loadBalance(currencyId) {
        const selectedOption = currencyField.querySelector(`option[value="${currencyId}"]`);
        const code = selectedOption?.getAttribute('data-code');
        const orderType = document.querySelector('[name="order_type"]').value;

        let currencyParam = currencyId;
        let currencyCodeParam = code;

        // Для крос-курсов используем выбранную версию базовой валюты (для покупки)
        // и всегда передаем оригинальный cross code (USD-EUR) при продаже, чтобы сервер показывал баланс quote (EUR).
        const isCross = isOptionCross(selectedOption);
        if (isCross) {
            const baseCurrencySelect = document.getElementById("base_currency");

            if (orderType === 'sell') {
                // При продаже отображаем баланс валюты quote (EUR)
                currencyCodeParam = code;
            } else if (baseCurrencySelect && baseCurrencySelect.style.display !== 'none' && baseCurrencySelect.value) {
                currencyParam = baseCurrencySelect.value;
                const selectedBaseCurrency = baseCurrencySelect.querySelector(`option[value="${baseCurrencySelect.value}"]`);
                currencyCodeParam = selectedBaseCurrency?.getAttribute('data-code') || code;
            }
        }

        fetch(`${balanceUrl}?currency=${currencyParam}&currency_code=${currencyCodeParam}&order_type=${orderType}`)
            .then(response => response.json())
            .then(data => {
                if (balanceEl) {
                    balanceEl.innerText = Number(data.balance).toLocaleString();
                }
            })


            .catch(err => console.error('Balance load error:', err));

    }

    if (currencyField) {
        currencyField.addEventListener("change", function () {
            loadBalance(this.value);
            updateCrossRateUI(this.value);
            calculate();
        });

        if (currencyField.value) {
            loadBalance(currencyField.value);
            updateCrossRateUI(currencyField.value);
        }
    }

    collectionBalances.forEach((balanceButton) => {
        balanceButton.addEventListener("click", function () {
            const item = this.closest(".collection-item");
            const amountRow = item?.querySelector(".collection-amount-row");
            const amountField = item?.querySelector(".collection-amount-input");
            const currencyIdField = item?.querySelector("input[name$='_currency_ids']");
            const isSelected = !amountRow?.classList.contains("hidden");

            amountRow?.classList.toggle("hidden", isSelected);
            amountField?.toggleAttribute("disabled", isSelected);
            currencyIdField?.toggleAttribute("disabled", isSelected);
            this.classList.toggle("bg-green-100", !isSelected);
            this.classList.toggle("text-green-700", !isSelected);
            this.classList.toggle("border-green-500", !isSelected);
            this.classList.toggle("dark:bg-green-500/20", !isSelected);
            this.classList.toggle("dark:text-green-400", !isSelected);
        });
    });

    // Слухаємо зміни order_type для оновлення label селекту базової валюти
    const orderTypeInput = document.querySelector('[name="order_type"]');
    if (orderTypeInput) {
        orderTypeInput.addEventListener("change", function () {
            const currencyId = currencyField.value;
            const selectedOption = currencyField.querySelector(`option[value="${currencyId}"]`);
            const code = selectedOption?.getAttribute('data-code');
            const isCross = isOptionCross(selectedOption);
            if (isCross) {
                updateCrossRateUI(currencyId);
                loadBalance(currencyId);
                console.log("code", code);
            }
        });
    }

});

// Функция для расчета эквивалента
function calculate() {
    const amountInput = document.getElementById("amount");
    const rateInput = document.getElementById("rate");
    const uahResult = document.getElementById("uah_result");
    const crossResult = document.getElementById("cross_result");
    const currencyField = document.querySelector("[name='currency']");
    const selectedOption = currencyField?.querySelector(`option[value="${currencyField.value}"]`);
    const code = selectedOption?.getAttribute('data-code');
    const isCross = isOptionCross(selectedOption);

    const crossInfo = isCross && code ? parseCrossRate(code) : null;

    if (crossInfo) {
        // Для кроссовых курсов: вычисляем курс и пересчитываем эквивалент
        const amount = parseFloat(amountInput?.value) || 0;
        const rate = parseFloat(rateInput?.value) || 0;
        const total = Math.round(amount * rate);
        if (crossResult) {
            crossResult.innerText = total.toLocaleString('ru-RU', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
    } else {
        // Для обычных курсов: эквивалент = сумма * курс
        const amount = parseFloat(amountInput?.value) || 0;
        const rate = parseFloat(rateInput?.value) || 0;
        const total = Math.round(amount * rate);
        if (uahResult) {
            uahResult.innerText = total.toLocaleString('ru-RU', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
    }
}

// Устанавливаем listener для input полей
document.addEventListener("DOMContentLoaded", function () {
    const amountInput = document.getElementById("amount");
    const rateInput = document.getElementById("rate");
    const clientGaveInput = document.getElementById("client_gave");

    if (amountInput) amountInput.addEventListener("input", function () {
        calculate();
        calculateMultiTotals();
    });
    if (rateInput) rateInput.addEventListener("input", function () {
        calculate();
        calculateMultiTotals();
    });
    if (clientGaveInput) clientGaveInput.addEventListener("input", function () {
        calculateMultiTotals();
    });

    // Інізіалізуємо мульти-підсумки при завантаженні
    calculateMultiTotals();
});

// ═══════════════════════════════════════════════════════════════════════════
// МУЛЬТИОПЕРАЦИИ: ДОБАВЛЕНИЕ СТРОК И РАСЧЕТ ИТОГОВ
// ═══════════════════════════════════════════════════════════════════════════

function addRow() {
    const container = document.getElementById('multi-rows');
    const rowIndex = container.children.length;

    const row = document.createElement('div');
    row.className = 'row flex gap-2 mb-3 p-3 bg-gray-50 dark:bg-base-700 rounded';
    row.dataset.rowId = rowIndex;

    row.innerHTML = `
        <div class="flex-1">
            <label class="block text-xs font-medium mb-1 text-gray-600 dark:text-gray-400">Валюта</label>
            <select name="multi_currency[]" class="multi-currency w-full border border-base-200 bg-white rounded px-3 py-2 dark:bg-base-900 dark:border-base-600 text-sm">
                <option value="">Обрати...</option>
                ${getCurrencyOptions()}
            </select>
        </div>
        <div class="flex-1">
            <label class="block text-xs font-medium mb-1 text-gray-600 dark:text-gray-400">Сума</label>
            <input type="number" step="0.01" name="multi_amount[]" class="multi-amount w-full border border-base-200 bg-white rounded px-3 py-2 dark:bg-base-900 dark:border-base-600 text-sm" placeholder="0.00">
        </div>
        <div class="flex-1">
            <label class="block text-xs font-medium mb-1 text-gray-600 dark:text-gray-400">Курс</label>
            <input type="number" step="0.001" name="multi_rate[]" class="multi-rate w-full border border-base-200 bg-white rounded px-3 py-2 dark:bg-base-900 dark:border-base-600 text-sm" placeholder="0.000">
        </div>
        <div class="flex items-end">
            <button type="button" onclick="removeRow(${rowIndex})" class="px-2 py-2 bg-red-100 text-red-600 rounded hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400 text-sm font-medium">
                ✕
            </button>
        </div>
    `;

    container.appendChild(row);

    // Добавляем слушатели для новых полей
    const currencySelect = row.querySelector('.multi-currency');
    const amountInput = row.querySelector('.multi-amount');
    const rateInput = row.querySelector('.multi-rate');

    if (currencySelect) {
        currencySelect.addEventListener('change', calculateMultiTotals);
    }
    if (amountInput) {
        amountInput.addEventListener('input', calculateMultiTotals);
    }
    if (rateInput) {
        rateInput.addEventListener('input', calculateMultiTotals);
    }

    calculateMultiTotals();
}

function removeRow(rowId) {
    const row = document.querySelector(`[data-row-id="${rowId}"]`);
    if (row) {
        row.remove();
        calculateMultiTotals();
    }
}

function getCurrencyOptions() {
    const currencyField = document.querySelector("[name='currency']");
    if (!currencyField) return '';

    return Array.from(currencyField.options)
        .filter(opt => opt.value !== '')
        .map(opt => {
            const code = opt.getAttribute('data-code') || '';
            const isCross = (opt.dataset && (opt.dataset.isCross === '1' || opt.dataset.isCross === 'true')) || (opt.getAttribute && !!(opt.getAttribute('data-code') || '').includes('-'));
            return `<option value="${opt.value}" data-code="${code}" data-is-cross="${isCross ? '1' : '0'}">${opt.textContent}</option>`;
        })
        .join('');
}

async function getCurrencyRate(currencyId) {
    try {
        const currencyField = document.querySelector("[name='currency']");
        const selectedOption = currencyField?.querySelector(`option[value="${currencyId}"]`);
        const code = selectedOption?.getAttribute('data-code') || '';

        // Извлекаем текущий курс из основного блока если это та же валюта
        const mainCurrencyId = currencyField?.value;
        if (mainCurrencyId === currencyId) {
            const rateInput = document.getElementById("rate");
            return parseFloat(rateInput?.value) || 0;
        }

        return 0;
    } catch (e) {
        console.error('Error getting currency rate:', e);
        return 0;
    }
}

function calculateMultiTotals() {
    const mainAmount = parseFloat(document.getElementById("amount")?.value) || 0;
    const mainRate = parseFloat(document.getElementById("rate")?.value) || 0;
    const mainCurrencySelect = document.querySelector("[name='currency']");
    const mainCurrencyId = mainCurrencySelect?.value;
    const mainCurrencyOption = mainCurrencySelect?.querySelector(`option[value="${mainCurrencyId}"]`);
    const mainCurrencyText = mainCurrencyOption?.textContent || "USD";

    // Оновлюємо основну операцію в сайдбарі
    const mainBadge = document.getElementById('main-currency-badge');
    if (mainBadge) mainBadge.textContent = mainCurrencyText;

    const mainAmountEl = document.getElementById('main-amount');
    if (mainAmountEl) mainAmountEl.textContent = mainAmount.toLocaleString('uk-UA', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    const mainRateEl = document.getElementById('main-rate');
    if (mainRateEl) mainRateEl.textContent = mainRate.toLocaleString('uk-UA', {
        minimumFractionDigits: 3,
        maximumFractionDigits: 3
    });

    // Главная валюта в гривнях
    let totalClientShould = mainAmount * mainRate;
    const mainTotal = document.getElementById('main-total');
    if (mainTotal) mainTotal.textContent = (mainAmount * mainRate).toLocaleString('uk-UA', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }) + ' ₴';

    // Добавляем итоги из дополнительных валют
    const multiRows = document.querySelectorAll('#multi-rows .row');
    let hasMultipleRows = multiRows.length > 0;

    // Оновлюємо додаткові операції
    const additionalItemsList = document.getElementById('additional-items-list');
    if (additionalItemsList) additionalItemsList.innerHTML = '';

    multiRows.forEach((row, index) => {
        const currencySelect = row.querySelector('.multi-currency');
        const amountInput = row.querySelector('.multi-amount');
        const rateInput = row.querySelector('.multi-rate');

        const currencyId = currencySelect?.value;
        const currencyOption = currencySelect?.querySelector(`option[value="${currencyId}"]`);
        const currencyText = currencyOption?.textContent || '';
        const amount = parseFloat(amountInput?.value) || 0;
        const rate = parseFloat(rateInput?.value) || 0;

        if (currencyId && amount && rate) {
            totalClientShould += amount * rate;

            // Додаємо до списку в сайдбарі
            const itemHtml = `
                <div class="flex justify-between items-start p-3 bg-gray-50 dark:bg-base-700 rounded-lg border border-gray-200 dark:border-base-600">
                    <div>
                        <div class="font-semibold text-gray-900 dark:text-gray-100 text-sm">${currencyText}</div>
                        <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            ${amount.toLocaleString('uk-UA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} × ${rate.toLocaleString('uk-UA', { minimumFractionDigits: 3, maximumFractionDigits: 3 })}
                        </div>
                    </div>
                    <div class="font-bold text-gray-900 dark:text-gray-100 text-right">
                        ${(amount * rate).toLocaleString('uk-UA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₴
                    </div>
                </div>
            `;

            if (additionalItemsList) {
                additionalItemsList.insertAdjacentHTML('beforeend', itemHtml);
            }
        } else if (currencyId && amount && !rate) {
            // Якщо курс не заповнен, блокуємо расчет
            hasMultipleRows = false;
        }
    });

    // Показуємо/ховаємо блок додаткових операцій
    const additionalOpsBlock = document.getElementById('additional-operations');
    if (additionalOpsBlock) {
        if (multiRows.length > 0) {
            additionalOpsBlock.classList.remove('hidden');
        } else {
            additionalOpsBlock.classList.add('hidden');
        }
    }

    // Получаем сумму, которую дал клиент
    const clientGaveInput = document.querySelector("[name='client_gave']");
    const clientGave = parseFloat(clientGaveInput?.value) || 0;

    const totalsBlock = document.getElementById('totals-sidebar');

    // Вычисляем итоги если: основная операция заполнена ИЛИ есть заполненные дополнительные операции
    const mainOperationReady = mainAmount && mainRate;
    const additionalOperationsReady = hasMultipleRows && multiRows.length > 0;

    if (mainOperationReady || additionalOperationsReady) {
        const change = clientGave - totalClientShould;

        document.getElementById('total-client-should').textContent =
            totalClientShould.toLocaleString('uk-UA', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }) + ' ₴';

        document.getElementById('total-client-gave').textContent =
            clientGave.toLocaleString('uk-UA', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }) + ' ₴';

        document.getElementById('total-change').textContent =
            change.toLocaleString('uk-UA', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }) + ' ₴';

        // Оновлюємо мобільний превью
        const mobilePreview = document.getElementById('mobile-total-preview');
        if (mobilePreview) {
            mobilePreview.textContent = totalClientShould.toLocaleString('uk-UA', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }) + ' ₴';
        }

        // Подсвечиваем сдачу красным если она отрицательная
        const changeElement = document.getElementById('total-change');
        if (changeElement) {
            changeElement.parentElement.classList.remove('bg-red-50', 'dark:bg-red-900/20', 'border-red-200', 'dark:border-red-900/50');
            changeElement.parentElement.classList.remove('bg-amber-50', 'dark:bg-amber-900/20', 'border-amber-200', 'dark:border-amber-900/50');
            changeElement.parentElement.querySelector('div').classList.remove('text-red-700', 'dark:text-red-400');
            changeElement.parentElement.querySelector('div').classList.remove('text-amber-700', 'dark:text-amber-400');

            if (change < 0) {
                changeElement.parentElement.classList.add('bg-red-50', 'dark:bg-red-900/20', 'border-red-200', 'dark:border-red-900/50');
                changeElement.parentElement.querySelector('div').classList.add('text-red-700', 'dark:text-red-400');
                changeElement.classList.remove('text-amber-600', 'dark:text-amber-400');
                changeElement.classList.add('text-red-600', 'dark:text-red-400');
            } else {
                changeElement.parentElement.classList.add('bg-amber-50', 'dark:bg-amber-900/20', 'border-amber-200', 'dark:border-amber-900/50');
                changeElement.parentElement.querySelector('div').classList.add('text-amber-700', 'dark:text-amber-400');
                changeElement.classList.remove('text-red-600', 'dark:text-red-400');
                changeElement.classList.add('text-amber-600', 'dark:text-amber-400');
            }
        }
    }
}

