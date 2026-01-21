<script lang="ts">
    import { invalidateAll } from '$app/navigation'; 

    export let data; // Now contains { course: { ..., modules: [] } }
    let fileInput: HTMLInputElement;
    let uploadStatus = "";

    async function handleUpload() {
        if (!fileInput.files || fileInput.files.length === 0) return;

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('course_id', data.course.id);

        uploadStatus = "Uploading...";

        const res = await fetch('http://127.0.0.1:5000/api/upload-mit-assignments', {
            method: 'POST',
            body: formData
        });

        const result = await res.json();
        
        if (res.ok) {
            uploadStatus = "Success!";
            fileInput.value = "";
            
            // THIS LINE IS MAGIC: It tells Svelte to re-run the 'load' function
            // effectively refreshing the list below instantly.
            await invalidateAll(); 
        } else {
            uploadStatus = "Error: " + result.error;
        }
    }
</script>

<div class="border p-4 rounded bg-white shadow-sm mt-6 mb-8">
    <h3 class="font-bold text-lg mb-2">Import MIT Assignments</h3>
    <div class="flex gap-2">
        <input type="file" accept=".html" bind:this={fileInput} class="border p-1 rounded" />
        <button on:click={handleUpload} class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            Upload
        </button>
    </div>
    {#if uploadStatus} <p class="mt-2 text-sm text-gray-600">{uploadStatus}</p> {/if}
</div>

<h2 class="text-2xl font-bold mb-4">Course Modules</h2>

{#if data.course.modules.length === 0}
    <p class="text-gray-500 italic">No modules found. Upload a syllabus above!</p>
{:else}
    <div class="grid gap-4">
        {#each data.course.modules as module}
            <div class="border rounded p-4 bg-white shadow-sm hover:shadow-md transition">
                <h4 class="font-bold text-lg text-blue-900">{module.title}</h4>
                <p class="text-gray-700 mt-2 whitespace-pre-wrap">{module.content}</p>
            </div>
        {/each}
    </div>
{/if}