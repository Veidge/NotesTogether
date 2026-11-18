<script setup lang="ts">
import {toTypedSchema} from '@vee-validate/zod'
import * as z from 'zod'
import {useForm} from "vee-validate"

const formSchema = toTypedSchema(
    z.object({
        username: z.string().min(3, "Имя пользователя должно содержать минимум 3 символа."),
        password: z.string().min(8, "Пароль должен содержать минимум 8 символов."),
    })
)

const form = useForm({
    validationSchema: formSchema,
})

const onSubmit = form.handleSubmit((values) => {
    console.log('Form submitted!', values)
})

const [username, usernameAttrs] = form.defineField('username');
const [password, passwordAttrs] = form.defineField('password');

</script>

<template>
    <div class="w-full min-h-screen flex items-center justify-center">
        <div class="w-[80%] md:w-[50%] lg:w-[40%] h-screen/2 md:h-screen/2.5 justify-items-center">
            <div class="w-full h-full rounded-[10px] bg-surface py-6 px-3">
                <form @submit="onSubmit">
                    <div class="flex flex-col gap-2">
                        <label for="username" class="p-2 mx-1">Имя пользователя</label>
                        <p class="mx-3 text-red-600"
                           v-if="form.errors.value.username && form.errors.value.username !== 'Required'">
                            {{ form.errors.value.username }}
                        </p>
                        <input id="username" class="p-2 mx-1 rounded-md border border-accent/60 outline-none
                        focus:ring-2 focus:ring-accent/30 transition-colors"
                               v-model="username" v-bind="usernameAttrs" type="text" placeholder="Введите имя пользователя"/>
                        <label for="password" class="p-2 mx-1">Пароль</label>
                        <p class="mx-3 text-red-600"
                           v-if="form.errors.value.password && form.errors.value.password !== 'Required'">
                            {{ form.errors.value.password }}
                        </p>
                        <input id="password" class="p-2 mx-1 rounded-md border border-accent/60 outline-none
                        focus:ring-2 focus:ring-accent/30 transition-colors"
                               v-model="password" v-bind="passwordAttrs" type="password" placeholder="Введите пароль"/>
                    </div>
                    <div class="flex justify-center mt-6">
                        <button type="submit" class="w-[45%] p-3 rounded-md bg-accent hover:bg-accent/80 active:bg-accent/60 cursor-pointer transition-colors">
                            Войти
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>
