let ITEMS_BY_ID = {};
let CART = {}; // item_id -> quantity

function fmt(n) {
  return window.CURRENCY_SYMBOL + n.toFixed(2);
}

async function loadItems() {
  const res = await fetch(window.ITEMS_FEED_URL);
  const items = await res.json();
  items.forEach((i) => (ITEMS_BY_ID[i.id] = i));
}

function addToCart(itemId) {
  const item = ITEMS_BY_ID[itemId];
  if (!item) return;
  const currentQty = CART[itemId] || 0;
  if (currentQty + 1 > item.available_qty) {
    alert(`Only ${item.available_qty} of "${item.name}" available.`);
    return;
  }
  CART[itemId] = currentQty + 1;
  renderCart();
}

function changeQty(itemId, delta) {
  const item = ITEMS_BY_ID[itemId];
  const newQty = (CART[itemId] || 0) + delta;
  if (newQty <= 0) {
    delete CART[itemId];
  } else if (newQty > item.available_qty) {
    alert(`Only ${item.available_qty} of "${item.name}" available.`);
    return;
  } else {
    CART[itemId] = newQty;
  }
  renderCart();
}

function removeFromCart(itemId) {
  delete CART[itemId];
  renderCart();
}

function computeTotals() {
  let subtotal = 0, discount = 0, tax = 0;
  Object.entries(CART).forEach(([id, qty]) => {
    const item = ITEMS_BY_ID[id];
    const gross = item.price * qty;
    const lineDiscount = gross * (item.discount_percent / 100);
    const taxable = gross - lineDiscount;
    const lineTax = taxable * (item.tax_percent / 100);
    subtotal += gross;
    discount += lineDiscount;
    tax += lineTax;
  });
  const grand = subtotal - discount + tax;
  return { subtotal, discount, tax, grand };
}

function renderCart() {
  const container = document.getElementById("cartLines");
  const entries = Object.entries(CART);

  if (entries.length === 0) {
    container.innerHTML = '<p class="text-muted" id="emptyCartMsg">No items added yet.</p>';
  } else {
    container.innerHTML = entries
      .map(([id, qty]) => {
        const item = ITEMS_BY_ID[id];
        const lineTotal = item.price * qty;
        return `
          <div class="cart-line">
            <div>
              <div>${item.name}</div>
              <div class="text-muted" style="font-size:11.5px;">
                <button type="button" class="btn btn-sm btn-outline-secondary py-0 px-1" onclick="changeQty(${id}, -1)">-</button>
                <span class="mx-1">${qty}</span>
                <button type="button" class="btn btn-sm btn-outline-secondary py-0 px-1" onclick="changeQty(${id}, 1)">+</button>
              </div>
            </div>
            <div class="text-end">
              <div>${fmt(lineTotal)}</div>
              <button type="button" class="btn btn-sm text-danger py-0 px-1" onclick="removeFromCart(${id})"><i class="bi bi-x"></i></button>
            </div>
          </div>`;
      })
      .join("");
  }

  const totals = computeTotals();
  document.getElementById("cartSubtotal").textContent = fmt(totals.subtotal);
  document.getElementById("cartDiscount").textContent = fmt(totals.discount);
  document.getElementById("cartTax").textContent = fmt(totals.tax);
  document.getElementById("cartGrand").textContent = fmt(totals.grand);

  document.getElementById("checkoutBtn").disabled = entries.length === 0;
}

document.getElementById("billForm").addEventListener("submit", function () {
  const cartPayload = Object.entries(CART).map(([id, qty]) => ({
    item_id: parseInt(id, 10),
    quantity: qty,
  }));
  document.getElementById("cartJson").value = JSON.stringify(cartPayload);
});

document.getElementById("itemSearch").addEventListener("input", filterItemGrid);
document.getElementById("categoryFilter").addEventListener("change", filterItemGrid);

function filterItemGrid() {
  const keyword = document.getElementById("itemSearch").value.toLowerCase();
  const categoryId = document.getElementById("categoryFilter").value;
  document.querySelectorAll(".item-tile").forEach((tile) => {
    const matchesName = tile.dataset.name.includes(keyword);
    const matchesCategory = !categoryId || tile.dataset.category === categoryId;
    tile.style.display = matchesName && matchesCategory ? "" : "none";
  });
}

loadItems();
