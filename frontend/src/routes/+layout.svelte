<script lang="ts">
    import '../app.css';
    import { onMount } from 'svelte';
    import { user } from '$lib/userStore';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';

    const API_URL = "https://canvasocegueda.pythonanywhere.com/api";

    onMount(async () => {
        // Check session with backend on every refresh
        try {
            const res = await fetch(`${API_URL}/check-session`, { credentials: 'include' });
            const data = await res.json();
            
            if (data.is_authenticated) {
                user.set({ username: data.username });
            } else {
                // If not logged in, and not already on login page, kick them out
                if ($page.url.pathname !== '/login') {
                    goto('/login');
                }
            }
        } catch (e) {
            console.error("Auth check failed");
        }
    });

    // Reactive Logout Function
    async function handleLogout() {
        await fetch(`${API_URL}/logout`, { method: 'POST', credentials: 'include' });
        user.set(null);
        goto('/login');
    }
</script>

<div class="min-h-screen bg-gray-50 text-gray-900 font-sans">
    {#if $user && $page.url.pathname !== '/login'}
        <nav class="bg-white border-b px-8 py-4 flex justify-between items-center shadow-sm">
            <div class="font-bold text-xl text-blue-900">MyLearning</div>
            <div class="flex items-center gap-4">
                <span class="text-gray-500 text-sm">Hi, {$user.username}</span>
                <button on:click={handleLogout} class="text-red-500 hover:text-red-700 text-sm font-medium">
                    Logout
                </button>
            </div>
        </nav>
    {/if}

    <slot />
</div>