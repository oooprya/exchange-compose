document.addEventListener('DOMContentLoaded', function () {
    const selector = document.getElementById('cashdeskSelector');
    const balancesNode = document.getElementById('cashdeskBalances');

    function getCsrf() {
        const el = document.querySelector('[name=csrfmiddlewaretoken]');
        return el ? el.value : null;
    }

    async function fetchBalances(shiftId, nodeId) {
        const url = `/wholesale/shift/${shiftId}/switch_cashdesk/`;
        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrf()
                },
                body: JSON.stringify({ node_id: nodeId })
            });

            const data = await res.json();
            if (!res.ok) {
                return { error: data.error || 'Ошибка при переключении кассы', ok: false };
            }
            return data;
        } catch (e) {
            console.error(e);
            return { error: 'Сетевая ошибка при переключении кассы', ok: false };
        }
    }

    function renderBalances(balances) {
        if (!balances || Object.keys(balances).length === 0) {
            balancesNode.innerHTML = '<div class="text-gray-400 text-sm">Нет данных по балансу</div>';
            return;
        }

        function showToast(message, type) {
            // type: 'success' | 'error'
            const id = 'cashdesk-toast';
            let el = document.getElementById(id);
            if (!el) {
                el = document.createElement('div');
                el.id = id;
                el.style.position = 'fixed';
                el.style.right = '20px';
                el.style.bottom = '20px';
                el.style.zIndex = 9999;
                document.body.appendChild(el);
            }

            const msg = document.createElement('div');
            msg.textContent = message;
            msg.style.marginTop = '8px';
            msg.style.padding = '10px 14px';
            msg.style.borderRadius = '8px';
            msg.style.minWidth = '180px';
            msg.style.boxShadow = '0 6px 18px rgba(0,0,0,0.12)';
            msg.style.color = '#fff';
            msg.style.fontWeight = '600';
            if (type === 'success') {
                msg.style.background = '#16a34a';
            } else {
                msg.style.background = '#dc2626';
            }

            el.appendChild(msg);
            setTimeout(() => {
                try { el.removeChild(msg); } catch (e) {}
                // remove container if empty
                if (el.childElementCount === 0) try { el.remove(); } catch (e) {}
            }, 3500);
        }

        const rows = Object.keys(balances).map(code => {
            const amount = balances[code];
            return `<div class="flex justify-between py-2 border-b last:border-0"><span class="font-medium text-gray-600">${code.toUpperCase()}</span><span class="font-bold text-green-600">${amount}</span></div>`;
        });

        balancesNode.innerHTML = rows.join('');
    }

    if (selector) {
        selector.addEventListener('change', async function (e) {
            const nodeId = this.value;
            // Получаем shift id из data-attr в селектор или из URL
            const shiftId = selector.getAttribute('data-shift-id') || window.CURRENT_SHIFT_ID;
            if (!shiftId) {
                alert('Не найдена текущая смена');
                return;
            }

            // UX: блокируем селектор и показываем индикатор
            selector.disabled = true;
            const original = selector.style.opacity;
            selector.style.opacity = '0.6';

            const result = await fetchBalances(shiftId, nodeId);

            selector.disabled = false;
            selector.style.opacity = original;

            if (!result) {
                showToast('Ошибка при переключении кассы', 'error');
                return;
            }

            if (result.ok === false || result.error) {
                showToast(result.error || 'Ошибка при переключении кассы', 'error');
                return;
            }

            if (result && result.success) {
                renderBalances(result.balances || {});
                showToast('Активная касса успешно изменена', 'success');
            }
        });

        // Установим data-shift-id если есть в DOM (попробуем найти скрытое поле)
        const shiftInput = document.querySelector('input[name="current_shift_id"]');
        if (shiftInput) selector.setAttribute('data-shift-id', shiftInput.value);
    }
});
