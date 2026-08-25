import { describe, it, expect, vi } from 'vitest'
import apiClient from './apiClient'
import { login, register, logout } from './authService'

vi.mock('./apiClient', () => ({ default: { post: vi.fn() } }))

describe('authService', () => {
  it('login posts credentials to /auth/login/', async () => {
    apiClient.post.mockResolvedValueOnce({ data: { user: { username: 'a' }, access: 'tok' } })
    const result = await login({ username: 'a', password: 'pw' })
    expect(apiClient.post).toHaveBeenCalledWith('/auth/login/', { username: 'a', password: 'pw' })
    expect(result.access).toBe('tok')
  })

  it('register posts to /auth/register/', async () => {
    apiClient.post.mockResolvedValueOnce({ data: { user: { username: 'b' }, access: 'tok2' } })
    await register({ username: 'b', email: 'b@example.com', password: 'pw' })
    expect(apiClient.post).toHaveBeenCalledWith('/auth/register/', { username: 'b', email: 'b@example.com', password: 'pw' })
  })

  it('logout posts to /auth/logout/', async () => {
    apiClient.post.mockResolvedValueOnce({})
    await logout()
    expect(apiClient.post).toHaveBeenCalledWith('/auth/logout/')
  })
})