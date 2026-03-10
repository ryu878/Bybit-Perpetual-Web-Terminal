import { useState, useCallback } from 'react'
import { apiPost } from '../api/client'
import type { OrderResponse } from '../types/api'
import { useWalletBalance } from '../hooks/useWalletBalance'

function randomFourDigitCode(): string {
  return String(Math.floor(1000 + Math.random() * 9000))
}

interface OrderPanelProps {
  symbol: string
  onOrderPlaced?: () => void
}

export default function OrderPanel({ symbol, onOrderPlaced }: OrderPanelProps) {
  const [qty, setQty] = useState('')
  const [loading, setLoading] = useState(false)
  const { data: walletBalance, loading: walletLoading, reload: reloadWallet } = useWalletBalance()
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [closeAllModal, setCloseAllModal] = useState<{ code: string } | null>(null)
  const [closeAllCodeInput, setCloseAllCodeInput] = useState('')
  const [closeAllError, setCloseAllError] = useState<string | null>(null)
  const [closeAllLoading, setCloseAllLoading] = useState(false)

  const openCloseAllModal = useCallback(() => {
    setCloseAllModal({ code: randomFourDigitCode() })
    setCloseAllCodeInput('')
    setCloseAllError(null)
  }, [])

  const cancelCloseAll = useCallback(() => {
    setCloseAllModal(null)
    setCloseAllCodeInput('')
    setCloseAllError(null)
  }, [])

  const confirmCloseAll = useCallback(async () => {
    if (!closeAllModal) return
    if (closeAllCodeInput.trim() !== closeAllModal.code) {
      setCloseAllError('Code does not match. Try again.')
      return
    }
    setCloseAllError(null)
    setCloseAllLoading(true)
    try {
      await apiPost<{ closed: number }>('/trade/close-all', { symbol })
      setCloseAllModal(null)
      setCloseAllCodeInput('')
      setMessage({ type: 'success', text: 'All positions closed' })
      onOrderPlaced?.()
      reloadWallet()
    } catch (e) {
      setCloseAllError(e instanceof Error ? e.message : 'Close all failed')
    } finally {
      setCloseAllLoading(false)
    }
  }, [closeAllModal, closeAllCodeInput, symbol, onOrderPlaced])

  const submit = async (side: 'Buy' | 'Sell') => {
    const q = qty.trim()
    if (!q || parseFloat(q) <= 0) {
      setMessage({ type: 'error', text: 'Enter a valid quantity' })
      return
    }
    setLoading(true)
    setMessage(null)
    try {
      await apiPost<OrderResponse>('/trade/order', { symbol, side, qty: q })
      setMessage({ type: 'success', text: `${side} order placed` })
      setQty('')
      onOrderPlaced?.()
      reloadWallet()
    } catch (e) {
      setMessage({ type: 'error', text: e instanceof Error ? e.message : 'Order failed' })
    } finally {
      setLoading(false)
    }
  }

  const closeSide = async (side: 'Buy' | 'Sell') => {
    const q = qty.trim()
    if (!q || parseFloat(q) <= 0) {
      setMessage({ type: 'error', text: 'Enter a valid quantity' })
      return
    }
    setLoading(true)
    setMessage(null)
    try {
      await apiPost<OrderResponse>('/trade/close', { symbol, side, qty: q })
      setMessage({ type: 'success', text: `Closed ${q} ${side}` })
      setQty('')
      onOrderPlaced?.()
      reloadWallet()
    } catch (e) {
      setMessage({ type: 'error', text: e instanceof Error ? e.message : 'Close failed' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="order-panel">
      <h3 className="order-panel__title">{symbol}</h3>
      <div className="order-panel__qty">
        <label>Quantity</label>
        <input
          type="text"
          inputMode="decimal"
          value={qty}
          onChange={(e) => setQty(e.target.value)}
          placeholder="0"
          disabled={loading}
        />
      </div>
      <div className="order-panel__buttons">
        <button
          type="button"
          className="order-panel__buy"
          disabled={loading}
          onClick={() => submit('Buy')}
        >
          {loading ? '…' : 'Buy'}
        </button>
        <button
          type="button"
          className="order-panel__sell"
          disabled={loading}
          onClick={() => submit('Sell')}
        >
          {loading ? '…' : 'Sell'}
        </button>
      </div>
      <hr className="order-panel__divider" />
      <div className="order-panel__close-buttons">
        <button
          type="button"
          className="order-panel__close-buy"
          disabled={loading}
          onClick={() => closeSide('Buy')}
        >
          {loading ? '…' : 'Close Buy'}
        </button>
        <button
          type="button"
          className="order-panel__close-sell"
          disabled={loading}
          onClick={() => closeSide('Sell')}
        >
          {loading ? '…' : 'Close Sell'}
        </button>
      </div>
      <hr className="order-panel__divider" />
      <div className="order-panel__close-all-wrap">
        <button
          type="button"
          className="order-panel__close-all"
          disabled={loading}
          onClick={openCloseAllModal}
        >
          Close All
        </button>
      </div>
      <hr className="order-panel__divider" />
      <div className="order-panel__margin-block">
        {walletLoading ? (
          <span className="order-panel__margin-loading">Loading…</span>
        ) : walletBalance ? (
          <>
            <div className="order-panel__margin-row">
              <span className="order-panel__margin-label">Initial Margin</span>
              <span className="order-panel__margin-value">{walletBalance.initial_margin_pct}%</span>
            </div>
            <div className="order-panel__margin-row">
              <span className="order-panel__margin-label">Maintenance Margin</span>
              <span className="order-panel__margin-value">{walletBalance.maintenance_margin_pct}%</span>
            </div>
            <div className="order-panel__margin-row">
              <span className="order-panel__margin-label">Margin Balance</span>
              <span className="order-panel__margin-value">
                {(Number(walletBalance.margin_balance) || 0).toFixed(4)} USDT
              </span>
            </div>
            <div className="order-panel__margin-row">
              <span className="order-panel__margin-label">Available Balance</span>
              <span className="order-panel__margin-value">
                {(Number(walletBalance.available_balance) || 0).toFixed(4)} USDT
              </span>
            </div>
          </>
        ) : null}
      </div>
      {closeAllModal && (
        <div className="order-panel__modal-overlay" role="dialog" aria-labelledby="close-all-title">
          <div className="order-panel__modal">
            <h4 id="close-all-title" className="order-panel__modal-title">Close all positions</h4>
            <p className="order-panel__modal-text">
              Are you sure? Enter the code <strong>{closeAllModal.code}</strong> and click Sure.
            </p>
            <input
              type="text"
              inputMode="numeric"
              maxLength={4}
              className="order-panel__modal-input"
              value={closeAllCodeInput}
              onChange={(e) => setCloseAllCodeInput(e.target.value.replace(/\D/g, ''))}
              placeholder="Code"
              disabled={closeAllLoading}
              autoFocus
            />
            {closeAllError && (
              <p className="order-panel__msg--err">{closeAllError}</p>
            )}
            <div className="order-panel__modal-buttons">
              <button
                type="button"
                className="order-panel__modal-cancel"
                disabled={closeAllLoading}
                onClick={cancelCloseAll}
              >
                Cancel
              </button>
              <button
                type="button"
                className="order-panel__modal-sure"
                disabled={closeAllLoading}
                onClick={confirmCloseAll}
              >
                {closeAllLoading ? '…' : 'Sure'}
              </button>
            </div>
          </div>
        </div>
      )}
      {message && (
        <p className={message.type === 'success' ? 'order-panel__msg--ok' : 'order-panel__msg--err'}>
          {message.text}
        </p>
      )}
    </div>
  )
}
