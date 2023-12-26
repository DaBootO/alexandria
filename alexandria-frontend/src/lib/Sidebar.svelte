<script>
    export let sidebarContent;
</script>

<div class="flex top-0 left-0 h-screen flex-col w-16 shadow-lg items-center">
    {#each sidebarContent as cnt}
        <div class="h-12">
            <button class="bg-slate-800 border-white justify-center text-sm m-2 w-8 h-8 rounded-xl hover:rounded-md hover:bg-slate-600 transition-all">
                <a href="/data-viewer">
                    {cnt}
                </a>
            </button>
        </div>
    {/each}
</div>
