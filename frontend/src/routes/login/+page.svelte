<script lang="ts">
    import { goto } from '$app/navigation';
    import { user } from '$lib/userStore';

    let isRegistering = false;
    let username = "";
    let password = "";
    let error = "";

    const API_URL = "https://canvasocegueda.pythonanywhere.com/api";

    async function handleSubmit() {
        error = "";
        const endpoint = isRegistering ? '/register' : '/login';
        
        try {
            // IMPORTANT: credentials: 'include' is what sends/saves the cookies!
            const res = await fetch(`${API_URL}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
                credentials: 'include' 
            });

            const data = await res.json();

            if (res.ok) {
                user.set({ username: data.username });
                goto('/'); // Redirect to dashboard
            } else {
                error = data.error || "Authentication failed";
            }
        } catch (e) {
            error = "Connection error. Check backend.";
        }
    }
</script>

<div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-md w-96">
        <h1 class="text-2xl font-bold mb-6 text-center text-blue-900">
            {isRegistering ? 'Create Account' : 'Welcome Back'}
        </h1>

        {#if error}
            <div class="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm">{error}</div>
        {/if}

        <form on:submit|preventDefault={handleSubmit} class="flex flex-col gap-4">
            <input 
                type="text" 
                bind:value={username} 
                placeholder="Username" 
                class="border p-2 rounded focus:ring-2 focus:ring-blue-500 outline-none"
                required
            />
            <input 
                type="password" 
                bind:value={password} 
                placeholder="Password" 
                class="border p-2 rounded focus:ring-2 focus:ring-blue-500 outline-none"
                required
            />
            <button class="bg-blue-600 text-white py-2 rounded hover:bg-blue-700 font-bold transition-colors">
                {isRegistering ? 'Sign Up' : 'Log In'}
            </button>
        </form>

        <p class="mt-4 text-center text-sm text-gray-600">
            {isRegistering ? 'Already have an account?' : 'Need an account?'}
            <button 
                class="text-blue-600 hover:underline font-medium" 
                on:click={() => { isRegistering = !isRegistering; error = ""; }}
            >
                {isRegistering ? 'Log In' : 'Register'}
            </button>
        </p>
    </div>
</div>