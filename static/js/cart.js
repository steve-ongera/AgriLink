/**
 * Cart functionality for Farm-to-Market platform
 * Handles AJAX cart operations
 */

// Get CSRF token
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value ||
           document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// Show notification message
function showNotification(message, type = 'success', duration = 5000) {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.cart-notification');
    existingNotifications.forEach(notif => notif.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `cart-notification alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px; 
        right: 20px; 
        z-index: 9999; 
        min-width: 300px; 
        max-width: 400px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    `;
    
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

// Update cart count in header/navbar
function updateCartCount(count) {
    const cartCountElements = document.querySelectorAll('.cart-count, .cart-counter, #cart-count');
    cartCountElements.forEach(element => {
        element.textContent = count;
        
        // Add animation effect
        element.style.transform = 'scale(1.3)';
        setTimeout(() => {
            element.style.transform = 'scale(1)';
        }, 200);
    });
    
    // Update cart badge visibility
    const cartBadges = document.querySelectorAll('.cart-badge');
    cartBadges.forEach(badge => {
        if (count > 0) {
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    });
}

// AJAX Add to Cart function - can be called from anywhere
function addToCart(productId, quantity = null) {
    // Get quantity from various sources
    if (!quantity) {
        // Try to get from quantity input on the same page
        const quantityInput = document.querySelector('#quantity, [name="quantity"], #form-quantity');
        quantity = quantityInput ? parseFloat(quantityInput.value) || 1 : 1;
    }
    
    // Show loading state
    const loadingButtons = document.querySelectorAll(`[onclick*="addToCart(${productId})"], .btn-add-cart`);
    const originalButtonStates = [];
    
    loadingButtons.forEach(btn => {
        originalButtonStates.push({
            element: btn,
            originalText: btn.innerHTML,
            originalDisabled: btn.disabled
        });
        
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Adding...';
    });
    
    // Make AJAX request
    fetch('/cart/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success notification
            showNotification(data.message, 'success');
            
            // Update cart count
            updateCartCount(data.cart_count);
            
            // Update any cart totals on the page
            const cartTotalElements = document.querySelectorAll('.cart-total');
            cartTotalElements.forEach(element => {
                element.textContent = `KES ${data.cart_total}`;
            });
            
        } else {
            // Show error notification
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Cart Error:', error);
        showNotification('Failed to add item to cart. Please try again.', 'error');
    })
    .finally(() => {
        // Restore button states
        originalButtonStates.forEach(state => {
            state.element.disabled = state.originalDisabled;
            state.element.innerHTML = state.originalText;
        });
    });
}

// Quick add to cart with confirmation (for product listing pages)
function quickAddToCart(productId, productName, quantity = 1) {
    addToCart(productId, quantity);
}

// Add to cart with custom quantity modal
function addToCartWithQuantity(productId, productName, minQuantity = 1, unit = 'kg') {
    // Create modal for quantity selection
    const modalHtml = `
        <div class="modal fade" id="quantityModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add to Cart</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <h6>${productName}</h6>
                        <div class="mb-3">
                            <label class="form-label">Quantity (${unit})</label>
                            <div class="input-group">
                                <button class="btn btn-outline-secondary" type="button" id="decreaseQty">-</button>
                                <input type="number" class="form-control text-center" id="modalQuantity" 
                                       value="${minQuantity}" min="${minQuantity}" step="${minQuantity}">
                                <button class="btn btn-outline-secondary" type="button" id="increaseQty">+</button>
                            </div>
                            <small class="text-muted">Minimum order: ${minQuantity} ${unit}</small>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-success" id="confirmAddToCart">Add to Cart</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('quantityModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('quantityModal'));
    modal.show();
    
    // Quantity controls
    const quantityInput = document.getElementById('modalQuantity');
    const decreaseBtn = document.getElementById('decreaseQty');
    const increaseBtn = document.getElementById('increaseQty');
    const confirmBtn = document.getElementById('confirmAddToCart');
    
    decreaseBtn.addEventListener('click', () => {
        const current = parseFloat(quantityInput.value);
        if (current > minQuantity) {
            quantityInput.value = current - minQuantity;
        }
    });
    
    increaseBtn.addEventListener('click', () => {
        const current = parseFloat(quantityInput.value);
        quantityInput.value = current + minQuantity;
    });
    
    confirmBtn.addEventListener('click', () => {
        const quantity = parseFloat(quantityInput.value);
        modal.hide();
        addToCart(productId, quantity);
    });
    
    // Clean up modal after hiding
    document.getElementById('quantityModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// Initialize cart functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Update cart count on page load
    fetch('/cart/count/')
        .then(response => response.json())
        .then(data => {
            updateCartCount(data.cart_count);
        })
        .catch(error => {
            console.log('Could not fetch cart count');
        });
    
    // Handle form-based add to cart submissions
    const cartForms = document.querySelectorAll('form[action*="add_to_cart"]');
    cartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const productId = formData.get('product_id');
            const quantity = parseFloat(formData.get('quantity')) || 1;
            
            addToCart(productId, quantity);
        });
    });
});

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-KE', {
        style: 'currency',
        currency: 'KES',
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    }).format(amount).replace('KES', 'KES ');
}

// Utility function to update product quantity inputs
function updateQuantityInput(productId, action) {
    const quantityInput = document.querySelector(`#quantity-${productId}, [data-product-id="${productId}"]`);
    if (!quantityInput) return;
    
    const current = parseFloat(quantityInput.value) || 1;
    const min = parseFloat(quantityInput.min) || 1;
    const step = parseFloat(quantityInput.step) || 1;
    
    if (action === 'increase') {
        quantityInput.value = current + step;
    } else if (action === 'decrease' && current > min) {
        quantityInput.value = Math.max(current - step, min);
    }
    
    // Trigger change event
    quantityInput.dispatchEvent(new Event('change'));
}

// Export functions for global use
window.addToCart = addToCart;
window.quickAddToCart = quickAddToCart;
window.addToCartWithQuantity = addToCartWithQuantity;
window.updateQuantityInput = updateQuantityInput;