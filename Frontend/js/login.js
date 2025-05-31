const API_URL = 'http://localhost:8000/auth';

// Default fetch options
const defaultFetchOptions = {
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
};

// Thêm biến để xác định loại trang login
const isAdminLogin = document.title === 'Admin Login';  // Hoặc kiểm tra một element đặc trưng của trang admin login

function toggleForms() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    if (loginForm.style.display === 'none') {
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    } else {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
    }
}

// Function đăng nhập cho user thường
async function login_user() {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const errorElement = document.getElementById('loginError');

    // Validate input
    if (!email || !password) {
        errorElement.textContent = 'Please fill in all fields';
        return;
    }

    try {
        console.log('Attempting user login with:', email);

        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            },
            body: formData
        });

        console.log('Response status:', response.status);
        const responseData = await response.json();
        console.log('Login response data:', responseData);

        if (response.ok) {
            const token = responseData.access_token;
            console.log('Token received:', token ? 'Yes' : 'No');
            
            // Store token in localStorage
            localStorage.setItem('access_token', token);
            
            // Get user info using the token
            const userResponse = await fetch(`${API_URL}/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/json'
                }
            });
            
            console.log('User info response status:', userResponse.status);
            
            if (userResponse.ok) {
                const userInfo = await userResponse.json();
                console.log('User info received:', userInfo);
                
                // Kiểm tra user type
                if (userInfo.type !== 'user') {
                    errorElement.textContent = 'Access denied. Please use admin login page.';
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('userInfo');
                    return;
                }
                
                // Store user info in localStorage
                localStorage.setItem('userInfo', JSON.stringify({
                    id: userInfo.id,
                    name: userInfo.name,
                    email: userInfo.email,
                    type: userInfo.type
                }));
                
                errorElement.textContent = '';
                alert('Login successful!');
                window.location.href = './booking.html';
            } else {
                const error = await userResponse.text();
                console.error('Failed to get user info:', error);
                errorElement.textContent = 'Failed to get user information';
            }
        } else {
            const error = responseData.detail || 'Login failed';
            console.error('Login failed:', error);
            errorElement.textContent = error;
        }
    } catch (error) {
        console.error('Login error:', error);
        errorElement.textContent = 'An error occurred. Please try again.';
    }
}

// Function đăng nhập cho admin
async function login_admin() {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const errorElement = document.getElementById('loginError');

    // Validate input
    if (!email || !password) {
        errorElement.textContent = 'Please fill in all fields';
        return;
    }

    try {
        console.log('Attempting admin login with:', email);

        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            },
            body: formData
        });

        console.log('Response status:', response.status);
        const responseData = await response.json();
        console.log('Login response data:', responseData);

        if (response.ok) {
            const token = responseData.access_token;
            console.log('Token received:', token ? 'Yes' : 'No');
            
            // Store token in localStorage
            localStorage.setItem('access_token', token);
            
            // Get user info using the token
            const userResponse = await fetch(`${API_URL}/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/json'
                }
            });
            
            console.log('User info response status:', userResponse.status);
            
            if (userResponse.ok) {
                const userInfo = await userResponse.json();
                console.log('User info received:', userInfo);
                
                // Kiểm tra user type
                if (userInfo.type !== 'admin') {
                    errorElement.textContent = 'Access denied. Admin privileges required.';
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('userInfo');
                    return;
                }
                
                // Store user info in localStorage
                localStorage.setItem('userInfo', JSON.stringify({
                    id: userInfo.id,
                    name: userInfo.name,
                    email: userInfo.email,
                    type: userInfo.type
                }));
                
                errorElement.textContent = '';
                alert('Login successful!');
                window.location.href = './admin.html';
            } else {
                const error = await userResponse.text();
                console.error('Failed to get user info:', error);
                errorElement.textContent = 'Failed to get user information';
            }
        } else {
            const error = responseData.detail || 'Login failed';
            console.error('Login failed:', error);
            errorElement.textContent = error;
        }
    } catch (error) {
        console.error('Login error:', error);
        errorElement.textContent = 'An error occurred. Please try again.';
    }
}

async function register() {
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const phone = document.getElementById('registerPhone').value;
    const dob = document.getElementById('registerDob').value;
    const type = 'user';
    const errorElement = document.getElementById('registerError');

    // Validate input
    if (!name || !email || !password || !phone || !dob) {
        errorElement.textContent = 'Please fill in all fields';
        return;
    }

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                name,
                email,
                password,
                phone_number: phone,
                date_of_birth: dob,
                type
            })
        });

        if (response.ok) {
            errorElement.textContent = '';
            alert('Registration successful! Please login.');
            toggleForms();
        } else {
            const error = await response.json();
            errorElement.textContent = error.detail || 'Registration failed';
        }
    } catch (error) {
        console.error('Registration error:', error);
        errorElement.textContent = 'An error occurred. Please try again.';
    }
}

// Add function to check if user is logged in
function isLoggedIn() {
    const token = localStorage.getItem('access_token');
    return !!token;
}

// Add function to logout
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('userInfo');
    window.location.href = 'login.html';
}

// Add function to get auth header for API calls
function getAuthHeader() {
    const token = localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}
