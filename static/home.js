
        const token = localStorage.getItem('token');

      
        if (!token) {
            window.location.href = '/';
        }

        const headers = { 'Authorization': `Bearer ${token}` };


        // GET /users/me → obtiene el usuario logueado y guarda su id
        async function loadMe() {
            const res = await fetch('/users/me', { headers });
            if (res.status === 401) { logout(); return; }
            const me = await res.json();
            window._myUserId = me.id;
        }

        // GET /users/ → read_users
        async function loadUsers() {
            try {
                const res = await fetch('/users/', { headers });
                if (res.status === 401) { logout(); return; }
                const users = await res.json();
                document.getElementById('users-table').innerHTML = users.map(u => `
                    <tr>
                        <td>${u.id}</td>
                        <td>${u.username}</td>
                        <td>${u.email}</td>
                        <td>${u.full_name || '-'}</td>
                    </tr>
                `).join('');
            } catch(e) {
                console.error('Error cargando usuarios:', e);
            }
        }

        // GET /items/ + GET /users/{id}/items/count → count_user_items
        async function loadItems() {
            try {
                const [itemsRes, countRes] = await Promise.all([
                    fetch('/items/', { headers }),
                    fetch(`/users/${window._myUserId}/items/count`, { headers }),
                ]);

                const items = await itemsRes.json();
                const countData = await countRes.json();

                document.getElementById('items-list').innerHTML =
                    items.map(i => `<tr>
                        <td>${i.id}</td>
                        <td>${i.title}</td>
                        <td>${i.cant}</td>
                    </tr>`).join('');

                document.getElementById('items-total').textContent =
                    `Total de items: ${countData.item_count ?? 0}`;
            } catch(e) {
                console.error('Error cargando items:', e);
            }
        }

        async function deleteUser() {
            const userId = document.getElementById('delete-user-id').value;
            const message = document.getElementById('delete-message');
            if (!userId) {message.textContent = 'Ingrese un usuario';return;}
            try {
                const res = await fetch(
                    `/users/${userId}`,
                    {
                        method: 'DELETE',
                        headers
                    }
                );
                console.log(res.status);
                if (res.ok) {
                
                    message.textContent =
                        'Usuario eliminado correctamente';
                    loadUsers();
                } else if(res.status === 404){
                    message.textContent ='No existe ese usuario';
                }
                else if (res.status === 400)
                 {
                       message.textContent =
                        'No puedes eliminarte a ti mismo';
                }
                else{
                    message.textContent = 'No se pudo eliminar el usuario';
                } 
            } catch(e) {
                message.textContent =
                    'Error eliminando usuario';
            }
        }

        async function createItem() {

            const title = document.getElementById(
                'item-title'
            ).value;

            const description = document.getElementById(
                'item-description'
            ).value;

            const message = document.getElementById(
                'create-item-message'
            );
            const cant = document.getElementById(
                'item-cant'
            ).value;

            if (!title) {
            
                message.textContent =
                    'Ingrese un título';
            
                return;
            }
        
            try {
            
                const res = await fetch(
                    '/items/',
                    {
                        method: 'POST',
                    
                        headers: {
                            ...headers,
                            'Content-Type': 'application/json'
                        },
                    
                        body: JSON.stringify({
                            title,
                            description,
                            cant                        })
                    }
                    
                );
                
                if (res.ok) {
                
                    message.textContent =
                        'Item creado correctamente';
                
                    document.getElementById(
                        'item-title'
                    ).value = '';
                
                    document.getElementById(
                        'item-description'
                    ).value = '';
                
                    loadItems();
                
                } else {
                
                    message.textContent =
                        'No se pudo crear el item';
                }
            
            } catch(e) {
            
                console.error(e);
            
                message.textContent =
                    'Error creando item';
            }
        }
        
        async function deleteItem() {
            const itemId = document.getElementById('delete-item-id').value;
            const message = document.getElementById('delete-item-message');
            if (!itemId) {message.textContent = 'Ingrese un item';return;}
            try {
                const res = await fetch(
                    `/items/${itemId}`,
                    {
                        method: 'DELETE',
                        headers
                    }
                );
                console.log(res.status);
                if (res.ok) {
                
                    message.textContent =
                        'Item eliminado correctamente';
                    loadItems();
                } else if(res.status === 404){
                    message.textContent ='No existe un Item con esa ID';
                }
                else{
                    message.textContent = 'No se pudo eliminar el Item';
                } 
            } catch(e) {
                message.textContent =
                    'Error eliminando Item';
            }
        }

        function logout() {
            localStorage.removeItem('token');
            window.location.href = '/';
        }

        const payload = JSON.parse(atob(token.split('.')[1]));

        document.getElementById('username-display').textContent = payload.sub;
        document.getElementById('user-info').textContent = payload.sub + ' | ';

        if (payload.role === 'admin') {
            document.getElementById('admin-controls').style.display = 'block';
        }

        // loadMe obtiene el id del usuario, luego loadUsers y loadItems corren en paralelo
        loadMe().then(() => Promise.all([loadUsers(), loadItems()]));