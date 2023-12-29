<script>
    import "../app.css";
</script>

<div>
    <div class="navbar bg-base-200">
        <div class="flex-1">
            <ul class="menu menu-horizontal px-1">
                <li>
                    <a href="/">Home</a>
                </li>
                <li>
                    <a href="/data-viewer">Data viewer</a>
                </li>
            </ul>
        </div>
    </div>

    <div class="flex">
        <slot />
    </div>
</div>
