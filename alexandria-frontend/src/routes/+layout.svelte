<script>
    import "../app.css";
</script>

<div>
    <div class="navbar bg-base-100">
        <div class="flex-1">
            <ul class="menu menu-horizontal px-1">
                <li>
                    <a href="/">Home</a>
                </li>
                <li>
                    <details>
                        <summary> Data Viewer </summary>
                        <ul class="p-2 bg-base-100 rounded-t-none">
                            <li>
                                <a href="/data-viewer">Table View</a>
                            </li>
                            <li>
                                <a href="/data-viewer">Node View</a>
                            </li>
                        </ul>
                    </details>
                </li>
            </ul>
        </div>
    </div>

    <div class="flex m-2">
        <slot />
    </div>
</div>
