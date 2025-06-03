// API endpoints
const API_BASE_URL = 'http://localhost:8000';
const BOOKINGS_URL = `${API_BASE_URL}/bookings`;

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('access_token');
    const userInfo = JSON.parse(localStorage.getItem('userInfo'));
    
    if (!token || !userInfo || userInfo.type !== 'user') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('userInfo');
        window.location.href = 'login.html';
        return;
    }
    
    document.getElementById('userInfo').textContent = `Welcome, ${userInfo.name}`;
}

// Logout function
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('userInfo');
    window.location.href = 'login.html';
}

// Load booking details
async function loadBookingDetails() {
    try {
        const bookingId = localStorage.getItem('currentBookingId');
        if (!bookingId) {
            window.location.href = 'booking.html';
            return;
        }

        const response = await fetch(`${BOOKINGS_URL}/${bookingId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = 'login.html';
                return;
            }
            throw new Error('Failed to load booking details');
        }

        const booking = await response.json();
        displayBookingDetails(booking);
    } catch (error) {
        console.error('Error loading booking details:', error);
        alert('Failed to load booking details');
    }
}

// Display booking details
function displayBookingDetails(booking) {
    const container = document.getElementById('bookingDetails');
    let total = 0;

    container.innerHTML = '';

    // Iterate over booking.booking_details which contains aggregated ticket info
    if (booking.booking_details && Array.isArray(booking.booking_details)) {
        booking.booking_details.forEach(detail => {
            // Each detail is an AggregatedBookingDetail with ticket_type and quantity
            const ticketType = detail.ticket_type;
            const quantity = detail.quantity;
            const subtotal = ticketType.price * quantity;
            total += subtotal;

            const div = document.createElement('div');
            div.className = 'ticket-item';
            div.innerHTML = `
                <div class="d-flex justify-content-between">
                    <div>
                        <h6>${ticketType.name}</h6>
                        <small class="text-muted">Quantity: ${quantity}</small>
                    </div>
                    <div>
                        <h6>$${subtotal.toFixed(2)}</h6>
                        <small class="text-muted">$${ticketType.price.toFixed(2)} each</small>
                    </div>
                </div>
            `;
            container.appendChild(div);
        });
    } else {
        container.innerHTML = '<p class="text-muted">No booking details found.</p>';
    }

    document.getElementById('totalAmount').textContent = `$${total.toFixed(2)}`;
}

// Confirm payment
async function confirmPayment() {
    try {
        const bookingId = localStorage.getItem('currentBookingId');
        if (!bookingId) {
            window.location.href = 'booking.html';
            return;
        }

        const response = await fetch(`${BOOKINGS_URL}/${bookingId}/confirm`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = 'login.html';
                return;
            }
            throw new Error('Failed to confirm payment');
        }

        alert('Payment confirmed successfully!');
        localStorage.removeItem('currentBookingId');
        window.location.href = 'booking.html';
    } catch (error) {
        console.error('Error confirming payment:', error);
        alert('Failed to confirm payment');
    }
}

// Cancel booking
async function cancelPayment() {
    try {
        const bookingId = localStorage.getItem('currentBookingId');
        if (!bookingId) {
            window.location.href = 'booking.html';
            return;
        }

        // Hiển thị confirm dialog
        if (!confirm('Are you sure you want to cancel this booking?')) {
            return;
        }

        const response = await fetch(`${BOOKINGS_URL}/${bookingId}/cancel`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = 'login.html';
                return;
            }
            throw new Error('Failed to cancel booking');
        }

        alert('Booking canceled successfully!');
        localStorage.removeItem('currentBookingId');
        window.location.href = 'booking.html';
    } catch (error) {
        console.error('Error canceling booking:', error);
        alert('Failed to cancel booking');
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadBookingDetails();
}); 